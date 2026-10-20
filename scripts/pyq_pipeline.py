"""
PYQ Ingestion and Verification Pipeline for GPAT 2010-2026.
Conforms strictly to Phase 2 Contract:
- Deterministic parsing with page-level provenance.
- Strict official key reconciliation (no guessing or AI key fabrication).
- Automated Quality Gate with review quarantine for malformed questions.
- Idempotent database insertion with SHA-256 fingerprinting.
"""

import os
import re
import json
import hashlib
import sqlite3
import pypdfium2
from typing import List, Dict, Any, Tuple, Optional

BASELINE_DB = "data/gpat_baseline.db"
LEARNER_DB = "gpat_knowledge.db"

QUALITY_PUBLISHED = "PUBLISHED"
QUALITY_NEEDS_CONTENT_REVIEW = "NEEDS_CONTENT_REVIEW"
QUALITY_NEEDS_KEY_REVIEW = "NEEDS_KEY_REVIEW"
QUALITY_REJECTED = "REJECTED"

ANSWER_VERIFIED = "VERIFIED"
ANSWER_MISSING = "MISSING_KEY"
ANSWER_CONFLICTING = "CONFLICTING_OR_DROPPED"

PROVENANCE_OFFICIAL = "OFFICIAL_PYQ"
RIGHTS_ACADEMIC = "ACADEMIC_FAIR_USE"

def compute_content_hash(stem: str, options: List[str]) -> str:
    norm_stem = re.sub(r'\s+', ' ', stem.strip().lower())
    norm_opts = "|".join([re.sub(r'\s+', ' ', o.strip().lower()) for o in options])
    raw = f"{norm_stem}::{norm_opts}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

class PYQPipeline:
    def __init__(self, pdf_path: str, paper_id: str, pyq_year: int, key_page: int):
        self.pdf_path = pdf_path
        self.paper_id = paper_id
        self.pyq_year = pyq_year
        self.key_page = key_page
        self.doc = pypdfium2.PdfDocument(pdf_path)

    def extract_answer_key(self) -> Tuple[Dict[int, str], int]:
        """
        Extracts official answer key from key_page strictly after Answer Key header.
        Returns mapping {q_number: key_str} and key_source_page.
        """
        kt = self.doc[self.key_page - 1].get_textpage().get_text_range()
        ak_idx = kt.find('Answer Key')
        if ak_idx == -1:
            ak_idx = kt.find('ANSWER KEY')
        ak_text = kt[ak_idx:] if ak_idx != -1 else kt
        matches = re.findall(r'(\d+)\s*[-–]\s*([a-dA-D\*\s&]+)', ak_text)
        key_map = {}
        for m in matches:
            q_num = int(m[0])
            key_val = m[1].strip().lower()
            key_map[q_num] = key_val
        return key_map, self.key_page

    def extract_questions_spatial(self, max_q: int = 125) -> List[Dict[str, Any]]:
        """
        Extracts questions using 2-column spatial bounding-box reconstruction.
        Handles complex multi-column newspaper layouts safely across GPAT 2010-2025.
        """
        key_map, key_page_num = self.extract_answer_key()
        all_text = ""
        page_offsets = []

        for p_idx in range(self.key_page):
            p = self.doc[p_idx]
            tp = p.get_textpage()
            n = tp.count_rects()
            rects = []
            key_y = 0

            if p_idx == self.key_page - 1:
                for i in range(n):
                    r = tp.get_rect(i)
                    text = tp.get_text_bounded(*r).strip()
                    if 'Answer Key' in text or 'ANSWER KEY' in text.upper():
                        key_y = r[3]
                        break

            for i in range(n):
                r = tp.get_rect(i)
                text = tp.get_text_bounded(*r).strip()
                if 50 <= r[1] <= 740 and text:
                    if p_idx == self.key_page - 1 and key_y > 0 and r[1] <= key_y:
                        continue
                    rects.append((r, text))

            left = [item for item in rects if item[0][0] < 306]
            right = [item for item in rects if item[0][0] >= 306]

            def sort_col(col):
                col.sort(key=lambda item: -item[0][3])
                lines = []
                curr = []
                last_top = None
                for r, text in col:
                    if last_top is None or abs(last_top - r[3]) <= 4.0:
                        curr.append((r[0], text))
                        if last_top is None:
                            last_top = r[3]
                    else:
                        curr.sort(key=lambda x: x[0])
                        lines.append(' '.join([x[1] for x in curr]))
                        curr = [(r[0], text)]
                        last_top = r[3]
                if curr:
                    curr.sort(key=lambda x: x[0])
                    lines.append(' '.join([x[1] for x in curr]))
                return '\n'.join(lines)

            page_offsets.append((len(all_text), p_idx + 1))
            all_text += f"\n--- [PAGE_{p_idx+1}] ---\n" + sort_col(left) + "\n" + sort_col(right)

        def get_page_for_pos(char_pos: int) -> int:
            page = 1
            for offset, p_num in page_offsets:
                if char_pos >= offset:
                    page = p_num
                else:
                    break
            return page

        extracted_records = []

        for q_num in range(1, max_q + 1):
            q_id = f"pyq_gpat_{self.pyq_year}_{q_num:03d}"
            next_num = q_num + 1

            pattern = rf'(?:^|\n)\s*{q_num}\.\s+(?:\*|\s)*(.*?)(?=(?:\n\s*{next_num}\.\s+(?:\*|\s)*[A-Za-z0-9])|--- \[PAGE_|$)'
            m = re.search(pattern, all_text, re.DOTALL)
            if not m:
                pattern = rf'(?:^|\n)\s*{q_num}\.\s+(?:\*|\s)*(.*?)(?=(?:\n\s*{next_num}\.\s+(?:\*|\s)*[A-Za-z0-9])|$)'
                m = re.search(pattern, all_text, re.DOTALL)

            if not m:
                extracted_records.append({
                    "q_id": q_id,
                    "original_q_number": q_num,
                    "paper_id": self.paper_id,
                    "pyq_year": self.pyq_year,
                    "source_page": 1,
                    "raw_text": None,
                    "stem": None,
                    "options": [],
                    "correct_option": None,
                    "answer_status": ANSWER_MISSING,
                    "quality_status": QUALITY_REJECTED,
                    "issues": ["QUESTION_STEM_NOT_FOUND"],
                    "key_source_page": key_page_num
                })
                continue

            start_pos = m.start()
            source_page = get_page_for_pos(start_pos)
            raw_block = m.group(1).strip()
            clean_block = re.sub(r'---\s*\[PAGE_\d+\]\s*---', '', raw_block).strip()

            a_pos = clean_block.find('(a)')
            issues = []

            if a_pos == -1:
                issues.append("MISSING_OPTION_A_MARKER")
                extracted_records.append({
                    "q_id": q_id,
                    "original_q_number": q_num,
                    "paper_id": self.paper_id,
                    "pyq_year": self.pyq_year,
                    "source_page": source_page,
                    "raw_text": clean_block,
                    "stem": clean_block,
                    "options": [],
                    "correct_option": None,
                    "answer_status": ANSWER_MISSING,
                    "quality_status": QUALITY_NEEDS_CONTENT_REVIEW,
                    "issues": issues,
                    "key_source_page": key_page_num
                })
                continue

            stem = clean_block[:a_pos].strip().replace('\r\n', ' ').replace('\n', ' ')
            stem = re.sub(r'\s+', ' ', stem)

            opt_matches = re.findall(r'\(([a-d])\)\s*(.*?)(?=\([a-d]\)|$)', clean_block[a_pos:], re.DOTALL)
            options = []
            for om in opt_matches:
                opt_str = om[1].strip().replace('\r\n', ' ').replace('\n', ' ')
                opt_str = re.sub(r'\s+', ' ', opt_str)
                options.append(opt_str)

            if len(options) != 4:
                issues.append(f"INVALID_OPTION_COUNT_{len(options)}")

            key_raw = key_map.get(q_num)
            correct_option_idx = None
            answer_status = ANSWER_VERIFIED

            if not key_raw:
                answer_status = ANSWER_MISSING
                issues.append("OFFICIAL_KEY_MISSING")
            elif '*' in key_raw or 'dropped' in key_raw:
                answer_status = ANSWER_CONFLICTING
                issues.append("QUESTION_DROPPED_OR_AMBIGUOUS_IN_OFFICIAL_KEY")
            elif '&' in key_raw or len(key_raw) > 1:
                answer_status = ANSWER_CONFLICTING
                issues.append(f"MULTIPLE_CORRECT_KEYS_{key_raw}")
            else:
                key_letter = key_raw.strip().lower()
                letter_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
                if key_letter in letter_map:
                    correct_option_idx = letter_map[key_letter]
                else:
                    answer_status = ANSWER_MISSING
                    issues.append(f"UNKNOWN_KEY_LETTER_{key_raw}")

            if issues:
                if any("MISSING" in i or "INVALID" in i for i in issues):
                    quality_status = QUALITY_NEEDS_CONTENT_REVIEW
                else:
                    quality_status = QUALITY_NEEDS_KEY_REVIEW
            else:
                quality_status = QUALITY_PUBLISHED

            content_hash = compute_content_hash(stem, options) if len(options) >= 2 else None

            extracted_records.append({
                "q_id": q_id,
                "original_q_number": q_num,
                "paper_id": self.paper_id,
                "pyq_year": self.pyq_year,
                "source_page": source_page,
                "raw_text": clean_block,
                "stem": stem,
                "options": options,
                "correct_option": correct_option_idx,
                "answer_status": answer_status,
                "quality_status": quality_status,
                "issues": issues,
                "key_source_page": key_page_num,
                "content_hash": content_hash
            })

        return extracted_records

    def extract_questions_linear(self, max_q: int = 125) -> List[Dict[str, Any]]:
        """
        Extracts questions from pages 1 to key_page - 1.
        Preserves question number, page provenance, raw text, and parsed options.
        """
        key_map, key_page_num = self.extract_answer_key()
        
        # Build page-indexed text (including key page up to ANSWER KEY)
        page_texts = []
        for p_idx in range(self.key_page):
            text = self.doc[p_idx].get_textpage().get_text_range()
            page_texts.append((p_idx + 1, text))

        combined_text = ""
        page_offsets = [] # (cumulative_char_index, page_number)
        for page_num, text in page_texts:
            page_offsets.append((len(combined_text), page_num))
            combined_text += f"\n--- [PAGE_{page_num}] ---\n" + text

        def get_page_for_pos(char_pos: int) -> int:
            page = 1
            for offset, p_num in page_offsets:
                if char_pos >= offset:
                    page = p_num
                else:
                    break
            return page

        extracted_records = []

        for q_num in range(1, max_q + 1):
            # Locate "N. "
            # Next boundary is "N+1. " or "--- [PAGE_" or "ANSWER KEY" or end
            next_num = q_num + 1
            pattern = rf'(?:^|\n)\s*{q_num}\.\s+(.*?)(?=(?:\n\s*{next_num}\.\s+[A-Za-z])|ANSWER KEY|$)'
            m = re.search(pattern, combined_text, re.DOTALL)
            
            q_id = f"pyq_gpat_{self.pyq_year}_{q_num:03d}"
            
            if not m:
                extracted_records.append({
                    "q_id": q_id,
                    "original_q_number": q_num,
                    "paper_id": self.paper_id,
                    "pyq_year": self.pyq_year,
                    "source_page": 1,
                    "raw_text": None,
                    "stem": None,
                    "options": [],
                    "correct_option": None,
                    "answer_status": ANSWER_MISSING,
                    "quality_status": QUALITY_REJECTED,
                    "issues": ["QUESTION_STEM_NOT_FOUND"],
                    "key_source_page": key_page_num
                })
                continue

            start_pos = m.start()
            source_page = get_page_for_pos(start_pos)
            raw_block = m.group(1).strip()
            
            # Clean headers/footers from raw block
            clean_block = re.sub(r'Website\s*-\s*www\.pharmacyindia\.co\.in.*?app from Playstore', '', raw_block, flags=re.DOTALL)
            clean_block = re.sub(r'GPAT\s*\d{4}\s*GPAT Competitive Exam.*?Pharmacy India', '', clean_block, flags=re.DOTALL)
            clean_block = re.sub(r'---\s*\[PAGE_\d+\]\s*---', '', clean_block)
            clean_block = clean_block.strip()

            # Find option (a)
            a_pos = clean_block.find('(a)')
            issues = []
            
            if a_pos == -1:
                issues.append("MISSING_OPTION_A_MARKER")
                extracted_records.append({
                    "q_id": q_id,
                    "original_q_number": q_num,
                    "paper_id": self.paper_id,
                    "pyq_year": self.pyq_year,
                    "source_page": source_page,
                    "raw_text": clean_block,
                    "stem": clean_block,
                    "options": [],
                    "correct_option": None,
                    "answer_status": ANSWER_MISSING,
                    "quality_status": QUALITY_NEEDS_CONTENT_REVIEW,
                    "issues": issues,
                    "key_source_page": key_page_num
                })
                continue

            stem = clean_block[:a_pos].strip().replace('\r\n', ' ').replace('\n', ' ')
            stem = re.sub(r'\s+', ' ', stem)

            # Extract options (a) through (d)
            opt_matches = re.findall(r'\(([a-d])\)\s*(.*?)(?=\([a-d]\)|$)', clean_block[a_pos:], re.DOTALL)
            options = []
            for om in opt_matches:
                opt_str = om[1].strip().replace('\r\n', ' ').replace('\n', ' ')
                opt_str = re.sub(r'\s+', ' ', opt_str)
                options.append(opt_str)

            # Option count validation
            if len(options) != 4:
                issues.append(f"INVALID_OPTION_COUNT_{len(options)}")

            # Key resolution
            key_raw = key_map.get(q_num)
            correct_option_idx = None
            answer_status = ANSWER_VERIFIED

            if not key_raw:
                answer_status = ANSWER_MISSING
                issues.append("OFFICIAL_KEY_MISSING")
            elif '*' in key_raw or 'dropped' in key_raw:
                answer_status = ANSWER_CONFLICTING
                issues.append("QUESTION_DROPPED_OR_AMBIGUOUS_IN_OFFICIAL_KEY")
            elif '&' in key_raw or len(key_raw) > 1:
                answer_status = ANSWER_CONFLICTING
                issues.append(f"MULTIPLE_CORRECT_KEYS_{key_raw}")
            else:
                key_letter = key_raw.strip().lower()
                letter_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
                if key_letter in letter_map:
                    correct_option_idx = letter_map[key_letter]
                else:
                    answer_status = ANSWER_MISSING
                    issues.append(f"UNKNOWN_KEY_LETTER_{key_raw}")

            # Determine quality status
            if issues:
                if any("MISSING" in i or "INVALID" in i for i in issues):
                    quality_status = QUALITY_NEEDS_CONTENT_REVIEW
                else:
                    quality_status = QUALITY_NEEDS_KEY_REVIEW
            else:
                quality_status = QUALITY_PUBLISHED

            content_hash = compute_content_hash(stem, options) if len(options) >= 2 else None

            extracted_records.append({
                "q_id": q_id,
                "original_q_number": q_num,
                "paper_id": self.paper_id,
                "pyq_year": self.pyq_year,
                "source_page": source_page,
                "raw_text": clean_block,
                "stem": stem,
                "options": options,
                "correct_option": correct_option_idx,
                "answer_status": answer_status,
                "quality_status": quality_status,
                "issues": issues,
                "key_source_page": key_page_num,
                "content_hash": content_hash
            })

        return extracted_records

def ingest_pyq_batch(records: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, int]:
    """
    Ingests extracted records transactionally into baseline database and review queue.
    Publishes only records with quality_status == QUALITY_PUBLISHED.
    Quarantines review items into pyq_review_queue.
    """
    stats = {
        "total_extracted": len(records),
        "published": 0,
        "quarantined": 0,
        "duplicates_skipped": 0
    }

    if dry_run:
        for r in records:
            if r["quality_status"] == QUALITY_PUBLISHED:
                stats["published"] += 1
            else:
                stats["quarantined"] += 1
        return stats

    base_conn = sqlite3.connect(BASELINE_DB)
    learn_conn = sqlite3.connect(LEARNER_DB)
    base_cur = base_conn.cursor()
    learn_cur = learn_conn.cursor()

    try:
        base_cur.execute("BEGIN TRANSACTION")
        learn_cur.execute("BEGIN TRANSACTION")

        for r in records:
            if r["quality_status"] == QUALITY_PUBLISHED:
                # Insert into baseline_questions
                base_cur.execute("""
                INSERT OR REPLACE INTO baseline_questions (
                    id, concept_id, topic_id, question_type, cognitive_level, difficulty,
                    question_text, media_id, options_json, correct_option, distractor_reasons_json,
                    explanation, source_page, provenance, verification_status, duplicate_fingerprint,
                    cue, pyq_year, paper_id, quality_status, raw_text, original_q_number,
                    answer_status, answer_source_page, rights_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["q_id"], "pk_absorption", f"pharmacology__pk_absorption",
                    "single_choice", "application", 7,
                    r["stem"], None, json.dumps(r["options"]), r["correct_option"],
                    json.dumps({}), f"Official GPAT {r['pyq_year']} question from {r['paper_id']}, page {r['source_page']}.",
                    r["source_page"], PROVENANCE_OFFICIAL, "VERIFIED", r["content_hash"],
                    f"GPAT {r['pyq_year']} Q{r['original_q_number']}", r["pyq_year"], r["paper_id"],
                    r["quality_status"], r["raw_text"], r["original_q_number"],
                    r["answer_status"], r["key_source_page"], RIGHTS_ACADEMIC
                ))

                # Also insert into gpat_knowledge.db questions table for runtime practice
                learn_cur.execute("""
                INSERT OR REPLACE INTO questions (
                    id, concept_id, question_type, difficulty, question_text,
                    options_json, correct_option, distractor_reasons_json,
                    explanation, source_page, cue
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["q_id"], "pk_absorption", "single_choice", 7,
                    r["stem"], json.dumps(r["options"]), r["correct_option"],
                    json.dumps({}), f"Official GPAT {r['pyq_year']} question from {r['paper_id']}.",
                    r["source_page"], f"GPAT {r['pyq_year']} Q{r['original_q_number']}"
                ))

                stats["published"] += 1
            else:
                # Route to review queue in baseline database
                review_id = f"rev_{r['q_id']}"
                base_cur.execute("""
                INSERT OR REPLACE INTO pyq_review_queue (
                    review_id, question_id, paper_id, pyq_year, original_q_number,
                    source_page, issue_type, details_json, raw_text, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    review_id, r["q_id"], r["paper_id"], r["pyq_year"], r["original_q_number"],
                    r["source_page"], ",".join(r["issues"]), json.dumps(r["issues"]),
                    r["raw_text"], "PENDING_REVIEW"
                ))
                stats["quarantined"] += 1

        base_conn.commit()
        learn_conn.commit()
    except Exception as e:
        base_conn.rollback()
        learn_conn.rollback()
        raise e
    finally:
        base_conn.close()
        learn_conn.close()

    return stats
