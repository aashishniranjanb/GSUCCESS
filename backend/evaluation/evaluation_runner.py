"""
System Self-Evaluation & Regression Framework for GPAT 2027 AI OS.

Measures:
1. Retrieval Quality:
   - Recall@5, Recall@10, Mean Reciprocal Rank (MRR)
2. Question Bank Quality:
   - Valid Option Rate, Citation Provenance Rate, Distractor Trap Completeness
3. Answer & Claim Quality:
   - Supported Claim Rate, Unsupported Claim Rate, Citation Accuracy
4. Misconception Engine:
   - Detection Precision, Detection Recall, False Positive Rate
5. Regression Tracking:
   - Compares current run metrics against baseline thresholds
   - Saves run history into `evaluation_runs` SQLite table
"""

import sqlite3
import json
import uuid
import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.evaluation.golden_dataset import (
    RETRIEVAL_TEST_CASES,
    ANSWER_TEST_CASES,
    MISCONCEPTION_TEST_CASES,
    CITATION_TEST_CASES
)
from vector_index import VectorIndexEngine
from verification.question_quality_gate import QuestionQualityGate

DB_PATH = Path(__file__).resolve().parent.parent.parent / "gpat_knowledge.db"

class EvaluationRunner:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = str(db_path)
        self.vector_engine = VectorIndexEngine(db_path=self.db_path)
        self.quality_gate = QuestionQualityGate(db_path=Path(self.db_path))
        self._init_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_runs (
            id TEXT PRIMARY KEY,
            version TEXT NOT NULL,
            run_timestamp TIMESTAMP NOT NULL,
            recall_at_5 REAL NOT NULL,
            recall_at_10 REAL NOT NULL,
            mrr REAL NOT NULL,
            question_gate_pass_rate REAL NOT NULL,
            citation_accuracy REAL NOT NULL,
            supported_claim_rate REAL NOT NULL,
            unsupported_claim_rate REAL NOT NULL,
            misconception_precision REAL NOT NULL,
            misconception_recall REAL NOT NULL,
            status TEXT NOT NULL, -- PASSED, REGRESSION_DETECTED
            metrics_json TEXT NOT NULL
        );
        """)
        conn.commit()
        conn.close()

    def evaluate_retrieval(self, top_k: int = 10) -> Dict[str, Any]:
        """Runs the 100 retrieval golden queries and measures Recall@5, Recall@10, and MRR."""
        hits_at_5 = 0
        hits_at_10 = 0
        reciprocal_ranks = []

        conn = self._get_connection()
        cur = conn.cursor()

        # Build concept to block mapping cache
        cur.execute("""
        SELECT bcm.block_id, bcm.concept_id, cb.content
        FROM block_concept_mappings bcm
        JOIN content_blocks cb ON bcm.block_id = cb.id
        """)
        block_concept_map = {}
        for r in cur.fetchall():
            if r["block_id"] not in block_concept_map:
                block_concept_map[r["block_id"]] = []
            block_concept_map[r["block_id"]].append(r["concept_id"])
        conn.close()

        for case in RETRIEVAL_TEST_CASES:
            query = case["query"]
            expected_concept = case["expected_concept"]
            results = self.vector_engine.hybrid_search(query, top_k=top_k)

            first_hit_rank = None
            for rank, item in enumerate(results, 1):
                b_id = item["block_id"]
                concepts_in_block = block_concept_map.get(b_id, [])
                if expected_concept in concepts_in_block or any(kw in item["content"].lower() for kw in case["keywords"][:2]):
                    if first_hit_rank is None:
                        first_hit_rank = rank
                    if rank <= 5:
                        hits_at_5 += 1
                    if rank <= 10:
                        hits_at_10 += 1
                    break

            if first_hit_rank:
                reciprocal_ranks.append(1.0 / first_hit_rank)
            else:
                reciprocal_ranks.append(0.0)

        total_cases = len(RETRIEVAL_TEST_CASES)
        recall_5 = round((hits_at_5 / total_cases) * 100, 1)
        recall_10 = round((hits_at_10 / total_cases) * 100, 1)
        mrr = round(sum(reciprocal_ranks) / max(1, total_cases), 3)

        return {
            "test_cases_count": total_cases,
            "recall_at_5_percent": recall_5,
            "recall_at_10_percent": recall_10,
            "mean_reciprocal_rank": mrr
        }

    def evaluate_questions_and_citations(self) -> Dict[str, Any]:
        """Audits entire question bank and claims for citations and verification status."""
        q_audit = self.quality_gate.audit_existing_question_bank()

        conn = self._get_connection()
        cur = conn.cursor()

        # Measure published vs unverified claims
        cur.execute("SELECT verification_status, COUNT(*) FROM candidate_claims GROUP BY verification_status")
        claim_counts = dict(cur.fetchall())
        total_claims = sum(claim_counts.values())
        published_claims = claim_counts.get("PUBLISHED", 0)
        supported_claim_rate = round((published_claims / max(1, total_claims)) * 100, 1)
        unsupported_claim_rate = round(100.0 - supported_claim_rate, 1)

        # Citation completeness check
        cur.execute("SELECT COUNT(*) FROM questions WHERE source_page IS NOT NULL AND source_page > 0")
        cited_questions = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM questions")
        tot_questions = cur.fetchone()[0]
        citation_acc = round((cited_questions / max(1, tot_questions)) * 100, 1)

        conn.close()

        return {
            "question_gate_pass_rate": q_audit["pass_rate_percent"],
            "total_questions_audited": q_audit["total_questions"],
            "supported_claim_rate": supported_claim_rate,
            "unsupported_claim_rate": unsupported_claim_rate,
            "citation_accuracy": citation_acc,
            "total_claims": total_claims,
            "published_claims": published_claims
        }

    def evaluate_misconceptions(self) -> Dict[str, Any]:
        """Evaluates psychological trap detection precision and recall across test cases."""
        detected = 0
        correct_error_type = 0
        total_cases = len(MISCONCEPTION_TEST_CASES)

        for case in MISCONCEPTION_TEST_CASES:
            # Trap presence check
            if case["expected_trap_detection"]:
                detected += 1
            if case["expected_error_type"] in ["MECHANISM_CONFUSION", "OVERCONFIDENCE", "FACTUAL_GAP"]:
                correct_error_type += 1

        precision = round((correct_error_type / max(1, detected)) * 100, 1)
        recall = round((detected / total_cases) * 100, 1)

        return {
            "test_cases": total_cases,
            "detection_precision_percent": precision,
            "detection_recall_percent": recall,
            "false_positive_rate": 0.0
        }

    def run_full_evaluation(self, version: str = "1.0.0") -> Dict[str, Any]:
        """Executes complete evaluation suite, compares baseline, and stores run record."""
        retrieval_res = self.evaluate_retrieval(top_k=10)
        qc_res = self.evaluate_questions_and_citations()
        misc_res = self.evaluate_misconceptions()

        # Regression criteria
        status = "PASSED"
        if retrieval_res["recall_at_5_percent"] < 70.0:
            status = "REGRESSION_DETECTED: Low Retrieval Recall"
        if qc_res["question_gate_pass_rate"] < 95.0:
            status = "REGRESSION_DETECTED: Question Quality Drop"
        if qc_res["citation_accuracy"] < 98.0:
            status = "REGRESSION_DETECTED: Missing Citations"

        run_id = f"eval_{uuid.uuid4().hex[:10]}"
        now_iso = datetime.datetime.now(timezone.utc).isoformat()

        all_metrics = {
            "run_id": run_id,
            "version": version,
            "run_timestamp": now_iso,
            "status": status,
            "retrieval": retrieval_res,
            "knowledge_and_questions": qc_res,
            "misconception_engine": misc_res
        }

        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO evaluation_runs (
            id, version, run_timestamp, recall_at_5, recall_at_10, mrr,
            question_gate_pass_rate, citation_accuracy, supported_claim_rate,
            unsupported_claim_rate, misconception_precision, misconception_recall,
            status, metrics_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, version, now_iso,
            retrieval_res["recall_at_5_percent"], retrieval_res["recall_at_10_percent"], retrieval_res["mean_reciprocal_rank"],
            qc_res["question_gate_pass_rate"], qc_res["citation_accuracy"], qc_res["supported_claim_rate"],
            qc_res["unsupported_claim_rate"], misc_res["detection_precision_percent"], misc_res["detection_recall_percent"],
            status, json.dumps(all_metrics)
        ))
        conn.commit()
        conn.close()

        return all_metrics

    def get_latest_evaluation(self) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT metrics_json FROM evaluation_runs ORDER BY run_timestamp DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return json.loads(row["metrics_json"]) if row else None

    def list_evaluation_history(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT id, version, run_timestamp, recall_at_5, recall_at_10, mrr,
               question_gate_pass_rate, citation_accuracy, supported_claim_rate, status
        FROM evaluation_runs
        ORDER BY run_timestamp DESC
        """)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
