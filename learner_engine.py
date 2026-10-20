"""
Adaptive Learning & Misconception Engine for GPAT 2027.
Implements:
1. Multi-factor Adaptive Scheduling Formula:
   Priority = memory_risk * exam_importance * weakness_multiplier * misconception_multiplier * recency_bonus
2. Confidence Calibration & Error Classification:
   - FACTUAL_GAP
   - MECHANISM_CONFUSION
   - DRUG_INTERACTION_RISK
   - OVERCONFIDENCE (High Confidence + Wrong)
   - FRAGILE_KNOWLEDGE (Low Confidence + Correct)
   - SOLID_MASTERY (High Confidence + Correct)
3. Learning Mode Filtering:
   - RECALL: Spaced retrieval across question matrix
   - REPAIR: Targeted misconception drill for recurring traps
   - EXAM: High-yield timed assessment
   - REVIEW: Strictly FSRS-due items
4. Prerequisite and Cognitive Stage Balancing:
   Recall -> Mechanism -> Application -> Discrimination
"""

import sqlite3
import json
import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
from fsrs import Scheduler, Card, Rating, State

DB_PATH = "gpat_knowledge.db"

# Canonical Misconception Categories
ERROR_FACTUAL_GAP = "FACTUAL_GAP"
ERROR_MECHANISM_CONFUSION = "MECHANISM_CONFUSION"
ERROR_DRUG_INTERACTION = "DRUG_INTERACTION_RISK"
ERROR_OVERCONFIDENCE = "OVERCONFIDENCE"
ERROR_CARELESS = "CARELESS_ERROR"

CALIBRATION_SOLID = "SOLID_MASTERY"          # Correct + High Confidence
CALIBRATION_FRAGILE = "FRAGILE_KNOWLEDGE"    # Correct + Low Confidence
CALIBRATION_GAP = "KNOWLEDGE_GAP"            # Incorrect + Low Confidence
CALIBRATION_MISCONCEPTION = "OVERCONFIDENT_MISCONCEPTION" # Incorrect + High Confidence

class LearnerEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.scheduler = Scheduler()
        self._init_tables()

    def _init_tables(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Student attempts table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS student_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            concept_id TEXT NOT NULL,
            selected_option INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            response_time_sec REAL NOT NULL,
            confidence INTEGER DEFAULT 3,
            hint_used INTEGER DEFAULT 0,
            calibration_category TEXT,
            error_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions(id),
            FOREIGN KEY (concept_id) REFERENCES concepts(id)
        );
        """)
        
        # Add columns to student_attempts if upgrading existing db
        cur.execute("PRAGMA table_info(student_attempts)")
        existing_cols = {r[1] for r in cur.fetchall()}
        if "calibration_category" not in existing_cols:
            cur.execute("ALTER TABLE student_attempts ADD COLUMN calibration_category TEXT")
        if "error_type" not in existing_cols:
            cur.execute("ALTER TABLE student_attempts ADD COLUMN error_type TEXT")

        # Concept memory state table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS concept_memory_state (
            student_id TEXT NOT NULL,
            concept_id TEXT NOT NULL,
            stability REAL DEFAULT 2.0,
            difficulty REAL DEFAULT 5.0,
            retrievability REAL DEFAULT 1.0,
            mastery REAL DEFAULT 0.0,
            attempts INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            misconception_count INTEGER DEFAULT 0,
            overconfidence_count INTEGER DEFAULT 0,
            last_review TIMESTAMP,
            next_review TIMESTAMP,
            PRIMARY KEY (student_id, concept_id),
            FOREIGN KEY (concept_id) REFERENCES concepts(id)
        );
        """)
        
        cur.execute("PRAGMA table_info(concept_memory_state)")
        cms_cols = {r[1] for r in cur.fetchall()}
        if "overconfidence_count" not in cms_cols:
            cur.execute("ALTER TABLE concept_memory_state ADD COLUMN overconfidence_count INTEGER DEFAULT 0")

        # Misconception records table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS student_misconceptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            concept_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            distractor_selected INTEGER NOT NULL,
            distractor_reason TEXT,
            error_type TEXT NOT NULL,
            occurrence_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'ACTIVE', -- ACTIVE, REPAIRED, RECURRING
            first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        );
        """)

        # FSRS cards per item/question
        cur.execute("""
        CREATE TABLE IF NOT EXISTS fsrs_cards (
            card_id INTEGER PRIMARY KEY,
            student_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            item_type TEXT DEFAULT 'question',
            state INTEGER NOT NULL,
            step INTEGER NOT NULL,
            stability REAL NOT NULL,
            difficulty REAL NOT NULL,
            due TIMESTAMP NOT NULL,
            last_review TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        conn.close()

    def get_or_create_fsrs_card(self, student_id: str, item_id: str, item_type: str = "question", cur = None):
        own_conn = False
        if cur is None:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            own_conn = True
            
        cur.execute("""
        SELECT card_id, state, step, stability, difficulty, due, last_review
        FROM fsrs_cards
        WHERE student_id = ? AND item_id = ? AND item_type = ?
        """, (student_id, item_id, item_type))
        
        row = cur.fetchone()
        
        if row:
            card_id, state_val, step, stability, difficulty, due_str, last_rev_str = row
            card = Card()
            card.card_id = card_id
            card.state = State(state_val)
            card.step = step
            card.stability = stability
            card.difficulty = difficulty
            card.due = datetime.datetime.fromisoformat(due_str) if isinstance(due_str, str) else due_str
            card.last_review = datetime.datetime.fromisoformat(last_rev_str) if isinstance(last_rev_str, str) and last_rev_str else None
        else:
            card = Card()
            cur.execute("""
            INSERT INTO fsrs_cards (card_id, student_id, item_id, item_type, state, step, stability, difficulty, due, last_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                card.card_id,
                student_id,
                item_id,
                item_type,
                card.state.value,
                card.step,
                card.stability or 0.0,
                card.difficulty or 0.0,
                card.due.isoformat(),
                card.last_review.isoformat() if card.last_review else None
            ))
            if own_conn:
                conn.commit()
                
        if own_conn:
            conn.close()
        return card

    def classify_calibration_and_error(self, is_correct: bool, confidence: int, response_time_sec: float, distractor_reason: Optional[str]) -> tuple:
        """
        Classifies confidence calibration quadrant and assigns educational error taxonomy.
        """
        if is_correct:
            if confidence >= 4:
                calibration = CALIBRATION_SOLID
            else:
                calibration = CALIBRATION_FRAGILE
            error_type = None
        else:
            if confidence >= 4:
                calibration = CALIBRATION_MISCONCEPTION
                error_type = ERROR_OVERCONFIDENCE
            else:
                calibration = CALIBRATION_GAP
                if response_time_sec < 8.0:
                    error_type = ERROR_CARELESS
                elif distractor_reason and ("mechanism" in distractor_reason.lower() or "receptor" in distractor_reason.lower()):
                    error_type = ERROR_MECHANISM_CONFUSION
                elif distractor_reason and ("contraindicated" in distractor_reason.lower() or "toxic" in distractor_reason.lower()):
                    error_type = ERROR_DRUG_INTERACTION
                else:
                    error_type = ERROR_FACTUAL_GAP
                    
        return calibration, error_type

    def record_attempt(self, student_id: str, question_id: str, selected_option: int, response_time_sec: float, confidence: int = 3, hint_used: int = 0, cur: Optional[sqlite3.Cursor] = None):
        own_conn = False
        if cur is None:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            own_conn = True
        else:
            conn = cur.connection
        
        cur.execute("SELECT concept_id, question_type, correct_option, distractor_reasons_json, explanation, source_page, cue FROM questions WHERE id = ?", (question_id,))
        q_row = cur.fetchone()
        if not q_row:
            if own_conn:
                conn.close()
            raise ValueError(f"Question {question_id} not found.")
            
        concept_id, q_type, correct_option, distractor_reasons_json, explanation, source_page, cue = q_row
        is_correct = int(selected_option == correct_option)
        distractor_reasons = json.loads(distractor_reasons_json)
        distractor_reason = distractor_reasons.get(str(selected_option), None) if not is_correct else None
        
        # 1. Calibration and Error Classification
        calibration, error_type = self.classify_calibration_and_error(
            bool(is_correct), confidence, response_time_sec, distractor_reason
        )
        
        # Insert attempt
        cur.execute("""
        INSERT INTO student_attempts (
            student_id, question_id, concept_id, selected_option, is_correct,
            response_time_sec, confidence, hint_used, calibration_category, error_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, question_id, concept_id, selected_option, is_correct, response_time_sec, confidence, hint_used, calibration, error_type))
        
        # Track Misconception record
        if not is_correct:
            cur.execute("""
            SELECT id, occurrence_count FROM student_misconceptions 
            WHERE student_id = ? AND concept_id = ? AND question_id = ? AND distractor_selected = ?
            """, (student_id, concept_id, question_id, selected_option))
            misc_row = cur.fetchone()
            now_iso = datetime.datetime.now(timezone.utc).isoformat()
            if misc_row:
                cur.execute("""
                UPDATE student_misconceptions
                SET occurrence_count = occurrence_count + 1,
                    status = 'RECURRING',
                    last_detected = ?
                WHERE id = ?
                """, (now_iso, misc_row[0]))
            else:
                cur.execute("""
                INSERT INTO student_misconceptions (student_id, concept_id, question_id, distractor_selected, distractor_reason, error_type, status, first_detected, last_detected)
                VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
                """, (student_id, concept_id, question_id, selected_option, distractor_reason or "Conceptual trap", error_type, now_iso, now_iso))
        else:
            # If student previously had an active misconception for this concept/question, resolve it
            cur.execute("""
            UPDATE student_misconceptions
            SET status = 'REPAIRED', resolved_at = ?
            WHERE student_id = ? AND concept_id = ? AND status IN ('ACTIVE', 'RECURRING')
            """, (datetime.datetime.now(timezone.utc).isoformat(), student_id, concept_id))

        # 2. Compute FSRS rating with Confidence Calibration:
        # High confidence + Wrong -> Again (penalty)
        # Low confidence + Wrong -> Again
        # Low confidence + Correct -> Hard (needs reinforcement)
        # Moderate confidence + Correct -> Good
        # High confidence + Correct + Fast (< 15s) -> Easy
        if not is_correct:
            fsrs_rating = Rating.Again
        else:
            if confidence >= 4 and response_time_sec < 15:
                fsrs_rating = Rating.Easy
            elif confidence <= 2 or response_time_sec > 40:
                fsrs_rating = Rating.Hard
            else:
                fsrs_rating = Rating.Good
                
        # Update FSRS card
        card = self.get_or_create_fsrs_card(student_id, question_id, item_type="question", cur=cur)
        updated_card, review_log = self.scheduler.review_card(card, fsrs_rating)
        
        cur.execute("""
        UPDATE fsrs_cards
        SET state = ?, step = ?, stability = ?, difficulty = ?, due = ?, last_review = ?
        WHERE card_id = ?
        """, (
            updated_card.state.value,
            updated_card.step or 0,
            updated_card.stability,
            updated_card.difficulty,
            updated_card.due.isoformat(),
            updated_card.last_review.isoformat() if updated_card.last_review else None,
            updated_card.card_id
        ))
        
        # 3. Update Concept Memory State
        cur.execute("""
        SELECT attempts, correct, misconception_count, overconfidence_count 
        FROM concept_memory_state 
        WHERE student_id = ? AND concept_id = ?
        """, (student_id, concept_id))
        c_row = cur.fetchone()
        
        attempts = (c_row[0] + 1) if c_row else 1
        correct = (c_row[1] + 1) if (c_row and is_correct) else (1 if is_correct else 0)
        misconceptions = (c_row[2] + (1 if not is_correct else 0)) if c_row else (1 if not is_correct else 0)
        overconf_add = 1 if (not is_correct and confidence >= 4) else 0
        overconf = (c_row[3] + overconf_add) if (c_row and c_row[3] is not None) else overconf_add
        
        mastery = round(correct / attempts, 2)
        retrievability = round(min(1.0, updated_card.stability / (updated_card.stability + 1.0)), 2)
        
        now_str = datetime.datetime.now(timezone.utc).isoformat()
        next_due = updated_card.due.isoformat()
        
        cur.execute("""
        INSERT INTO concept_memory_state (
            student_id, concept_id, stability, difficulty, retrievability,
            mastery, attempts, correct, misconception_count, overconfidence_count,
            last_review, next_review
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id, concept_id) DO UPDATE SET
            stability = excluded.stability,
            difficulty = excluded.difficulty,
            retrievability = excluded.retrievability,
            mastery = excluded.mastery,
            attempts = excluded.attempts,
            correct = excluded.correct,
            misconception_count = excluded.misconception_count,
            overconfidence_count = excluded.overconfidence_count,
            last_review = excluded.last_review,
            next_review = excluded.next_review
        """, (
            student_id, concept_id, updated_card.stability, updated_card.difficulty,
            retrievability, mastery, attempts, correct, misconceptions, overconf,
            now_str, next_due
        ))
        
        if own_conn:
            conn.commit()
            conn.close()
        
        feedback = {
            "is_correct": bool(is_correct),
            "selected_option": selected_option,
            "correct_option": correct_option,
            "distractor_reason": distractor_reason,
            "calibration_category": calibration,
            "error_type": error_type,
            "explanation": explanation,
            "source_page": source_page,
            "cue": cue,
            "fsrs_rating": fsrs_rating.name,
            "next_due_date": next_due,
            "concept_mastery": mastery,
            "stability_days": round(updated_card.stability, 2)
        }
        return feedback

    def generate_daily_session(self, student_id: str, session_minutes: int = 25, mode: str = "balanced") -> Dict[str, Any]:
        """
        Adaptive Session Scheduler using the unified priority formula:
        Priority = (FSRS Memory Risk) * (Exam Weight) * (Weakness Multiplier) * (Misconception Risk) * (Stage Alignment)
        
        Modes supported:
        - 'balanced': Daily mission (due reviews + misconception repair + high-yield new concepts)
        - 'repair': Focuses purely on active misconceptions and recurring traps
        - 'review': Purely FSRS-due items
        - 'exam': Timed clinical & application scenario questions
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Question count scaled to ~90s per retrieval task:
        # 5m -> ~3 questions (4.5 min)
        # 12m -> ~8 questions (12.0 min)
        # 25m -> ~16 questions (24.0 min)
        target_questions = max(3, round((session_minutes * 60) / 90))
        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        
        # 1. FSRS Due Items
        cur.execute("""
        SELECT item_id, due, stability
        FROM fsrs_cards
        WHERE student_id = ? AND item_type = 'question' AND due <= ?
        ORDER BY due ASC
        """, (student_id, now_iso))
        due_map = {r[0]: r[2] for r in cur.fetchall()}
        
        # 2. Concept Memory and Active Misconceptions
        cur.execute("""
        SELECT concept_id, mastery, misconception_count, overconfidence_count, retrievability
        FROM concept_memory_state
        WHERE student_id = ?
        """, (student_id,))
        concept_stats = {r[0]: {"mastery": r[1], "misc": r[2], "overconf": r[3], "retrievability": r[4]} for r in cur.fetchall()}
        
        cur.execute("""
        SELECT concept_id, COUNT(*) 
        FROM student_misconceptions 
        WHERE student_id = ? AND status IN ('ACTIVE', 'RECURRING')
        GROUP BY concept_id
        """, (student_id,))
        active_misc_concepts = {r[0]: r[1] for r in cur.fetchall()}
        
        # 3. Retrieve all questions from DB (enriching with media from baseline_media if present)
        cur.execute("""
        SELECT q.id, q.concept_id, q.question_type, q.difficulty, q.question_text,
               q.options_json, q.source_page, q.cue, c.name, c.importance_score,
               m.relative_file_path, m.alt_text, m.caption
        FROM questions q
        JOIN concepts c ON q.concept_id = c.id
        LEFT JOIN baseline_questions bq ON bq.id = q.id
        LEFT JOIN baseline_media m ON bq.media_id = m.media_id
        """)
        all_q = cur.fetchall()
        
        scored_questions = []
        for q in all_q:
            q_id, c_id, q_type, diff, q_text, opts_json, page, cue, c_name, importance, m_path, m_alt, m_cap = q
            
            c_data = concept_stats.get(c_id, {"mastery": 0.0, "misc": 0, "overconf": 0, "retrievability": 0.5})
            is_due = q_id in due_map
            has_active_misc = c_id in active_misc_concepts
            
            # --- Multi-factor Adaptive Scheduling Formula ---
            # Base importance from GPAT syllabus (1..10)
            base_importance = float(importance or 5)
            
            # Memory Risk Factor: 1.0 (new/safe) up to 3.0 (overdue)
            memory_risk = 1.0
            if is_due:
                memory_risk = 3.0
            elif c_data["mastery"] > 0:
                # Retrievability decay
                memory_risk = 1.0 + (1.0 - c_data["retrievability"]) * 1.5
                
            # Weakness Factor: Low mastery gets prioritized
            weakness_factor = 1.0
            if c_data["mastery"] < 0.5:
                weakness_factor = 2.0
            elif c_data["mastery"] < 0.75:
                weakness_factor = 1.4
                
            # Misconception Multiplier: Traps need immediate repair
            misc_multiplier = 1.0
            if has_active_misc:
                misc_multiplier = 2.5
            elif c_data["overconf"] > 0:
                misc_multiplier = 1.8
                
            # Mode-specific filters and weights
            mode_weight = 1.0
            if mode == "repair":
                if not has_active_misc and c_data["misc"] == 0:
                    continue
                mode_weight = 3.0
            elif mode == "review":
                if not is_due:
                    continue
                mode_weight = 3.0
            elif mode == "exam":
                if q_type not in ["clinical_scenario", "mcq_clinical", "application"]:
                    mode_weight = 0.5
            # Candidate Type & Diagnostic Reason Code
            candidate_type = "NEW_LEARNING"
            reason_codes = []
            if is_due:
                candidate_type = "DUE_REVIEW"
                reason_codes.append("OVERDUE_FSRS_REVIEW")
            elif has_active_misc:
                candidate_type = "TARGETED_REPAIR"
                reason_codes.append("RECURRING_MISCONCEPTION_TRAP")
            elif c_data.get("overconf", 0) > 0:
                candidate_type = "TARGETED_REPAIR"
                reason_codes.append("OVERCONFIDENCE_BIAS_DETECTED")
            elif c_data.get("mastery", 0) > 0 and c_data.get("mastery", 0) < 0.5:
                candidate_type = "TARGETED_REPAIR"
                reason_codes.append("WEAK_CONCEPT_REINFORCEMENT")
            elif q_id.startswith("pyq_"):
                candidate_type = "PYQ_PRACTICE"
                reason_codes.append("OFFICIAL_PYQ_PRACTICE")
            else:
                candidate_type = "NEW_LEARNING"
                reason_codes.append("HIGH_YIELD_SYLLABUS_CONCEPT")

            # Composite Priority
            priority = (base_importance * memory_risk * weakness_factor * misc_multiplier * mode_weight)
            
            # Media web URL formatting
            media_url = None
            if m_path:
                norm_p = m_path.replace("\\", "/")
                media_url = "/" + norm_p.replace("baseline/", "") if norm_p.startswith("baseline/") else "/" + norm_p

            scored_questions.append({
                "question_id": q_id,
                "concept_id": c_id,
                "concept_name": c_name,
                "question_type": q_type,
                "candidate_type": candidate_type,
                "reason_codes": reason_codes,
                "difficulty": diff,
                "importance": importance,
                "question_text": q_text,
                "options": json.loads(opts_json),
                "source_page": page,
                "cue": cue,
                "media_url": media_url,
                "media_alt": m_alt,
                "media_caption": m_cap,
                "priority_score": round(priority, 2),
                "is_due": is_due,
                "has_active_misconception": has_active_misc,
                "estimated_seconds": 90
            })
            
        scored_questions.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Fallback if specialized mode filter (e.g. repair or review) produced 0 candidates
        if not scored_questions and mode in ["repair", "review"]:
            # Fall back to high-yield questions so student can always study
            for q in all_q:
                q_id, c_id, q_type, diff, q_text, opts_json, page, cue, c_name, importance, m_path, m_alt, m_cap = q
                scored_questions.append({
                    "question_id": q_id,
                    "concept_id": c_id,
                    "concept_name": c_name,
                    "importance": importance,
                    "priority_score": float(importance or 5),
                    "is_due": False,
                    "has_active_misconception": False,
                    "candidate_type": "NEW_LEARNING",
                    "reason_codes": ["FALLBACK_HIGH_YIELD_PRACTICE"],
                    "estimated_seconds": 150,
                    "question_text": q_text,
                    "options": json.loads(opts_json),
                    "source_page": page,
                    "cue": cue,
                    "media_url": ("/" + m_path.replace("\\", "/").replace("baseline/", "")) if m_path else None,
                    "media_alt": m_alt,
                    "media_caption": m_cap
                })

        # Diversity Constraint: Max 2 consecutive questions on the same concept_id
        selected_questions = []
        concept_streak = {}
        deferred = []
        
        for q in scored_questions:
            c_id = q["concept_id"]
            if len(selected_questions) >= target_questions:
                break
            
            # Check last 2 selections
            if len(selected_questions) >= 2 and selected_questions[-1]["concept_id"] == c_id and selected_questions[-2]["concept_id"] == c_id:
                deferred.append(q)
                continue
                
            selected_questions.append(q)
            
        # Fill remaining slots if deferred exists
        if len(selected_questions) < target_questions and deferred:
            for q in deferred:
                if len(selected_questions) >= target_questions:
                    break
                selected_questions.append(q)
        
        # Categorized session timeline
        due_count = sum(1 for q in selected_questions if q["is_due"])
        misc_count = sum(1 for q in selected_questions if q["has_active_misconception"])
        new_count = len(selected_questions) - due_count - misc_count
        
        session_plan = {
            "session_time_minutes": session_minutes,
            "target_question_count": len(selected_questions),
            "mode": mode,
            "composition": {
                "due_recall_count": due_count,
                "misconception_repair_count": misc_count,
                "high_yield_concept_count": max(0, new_count)
            },
            "timeline": [
                {"block": "FSRS Spaced Retention", "duration_min": round(session_minutes * 0.35, 1)},
                {"block": "Misconception & Trap Repair", "duration_min": round(session_minutes * 0.35, 1)},
                {"block": "High-Yield Clinical Application", "duration_min": round(session_minutes * 0.30, 1)}
            ],
            "questions": selected_questions
        }
        
        conn.close()
        return session_plan

if __name__ == "__main__":
    engine = LearnerEngine()
    print("Adaptive LearnerEngine initialized.")
    session = engine.generate_daily_session("student_01", session_minutes=25)
    print(f"Generated Session: {session['target_question_count']} questions. Composition: {session['composition']}")
    for q in session["questions"][:5]:
        print(f"  * [{q['concept_id']}] ({q['question_type']}, Priority {q['priority_score']}): {q['question_text'][:75]}...")
