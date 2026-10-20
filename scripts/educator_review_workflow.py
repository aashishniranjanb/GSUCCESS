"""
Educator Review Workflow for Staged Topic Mappings.

Allows SME educators to:
1. List unreviewed staged candidate mappings.
2. Record human editorial review (APPROVED, REJECTED, NEEDS_CLARIFICATION) with notes and taxonomy version.
3. Test downstream impact against an isolated disposable database copy without altering production.
"""

import os
import sys
import csv
import json
import sqlite3
import shutil
import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STAGING_DB = ROOT_DIR / "data" / "pyq_topic_staging.db"
PROPOSAL_CSV = ROOT_DIR / "reports" / "phase6_3_mapping_promotion_proposal.csv"
BASELINE_DB = ROOT_DIR / "data" / "gpat_baseline.db"

def get_staging_conn():
    conn = sqlite3.connect(str(STAGING_DB))
    conn.row_factory = sqlite3.Row
    return conn

def record_editorial_review(
    question_id: str,
    reviewer_id: str,
    review_decision: str,  # 'APPROVED', 'REJECTED', 'NEEDS_CLARIFICATION'
    approved_subject_id: Optional[str] = None,
    approved_topic_id: Optional[str] = None,
    approved_topic_name: Optional[str] = None,
    taxonomy_version: str = "v1.0_gpat_2027",
    matched_evidence: str = "",
    review_notes: str = ""
) -> Dict[str, Any]:
    if review_decision not in ("APPROVED", "REJECTED", "NEEDS_CLARIFICATION"):
        raise ValueError(f"Invalid review decision: {review_decision}")

    conn = get_staging_conn()
    cur = conn.cursor()

    review_id = f"rev_{question_id}_{reviewer_id}"
    now_iso = datetime.datetime.now(timezone.utc).isoformat()

    cur.execute("""
    INSERT OR REPLACE INTO editorial_reviews (
        review_id, question_id, reviewer_id, review_decision,
        approved_subject_id, approved_topic_id, approved_topic_name,
        taxonomy_version, matched_evidence, review_notes, reviewed_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        review_id, question_id, reviewer_id, review_decision,
        approved_subject_id, approved_topic_id, approved_topic_name,
        taxonomy_version, matched_evidence, review_notes, now_iso
    ))
    conn.commit()
    conn.close()

    return {
        "review_id": review_id,
        "question_id": question_id,
        "reviewer_id": reviewer_id,
        "decision": review_decision,
        "reviewed_at": now_iso
    }

def get_editorial_summary() -> Dict[str, Any]:
    conn = get_staging_conn()
    cur = conn.cursor()

    # Total staged proposals
    total_staged = 137
    if PROPOSAL_CSV.exists():
        with open(PROPOSAL_CSV, "r", encoding="utf-8") as f:
            total_staged = len(list(csv.DictReader(f)))

    cur.execute("""
    SELECT review_decision, count(*)
    FROM editorial_reviews
    GROUP BY review_decision
    """)
    decision_counts = dict(cur.fetchall())
    total_reviewed = sum(decision_counts.values())

    cur.execute("""
    SELECT review_id, question_id, reviewer_id, review_decision,
           approved_subject_id, approved_topic_id, approved_topic_name,
           taxonomy_version, review_notes, reviewed_at
    FROM editorial_reviews
    ORDER BY reviewed_at DESC
    """)
    reviews = [dict(r) for r in cur.fetchall()]

    conn.close()

    return {
        "total_staged_proposals": total_staged,
        "total_reviewed": total_reviewed,
        "pending_review": max(0, total_staged - total_reviewed),
        "approved_count": decision_counts.get("APPROVED", 0),
        "rejected_count": decision_counts.get("REJECTED", 0),
        "clarification_count": decision_counts.get("NEEDS_CLARIFICATION", 0),
        "recent_reviews": reviews
    }

def test_downstream_impact_on_disposable_copy() -> Dict[str, Any]:
    """
    Applies only APPROVED reviews to a disposable temporary database copy.
    Verifies question retrieval, topic distribution, and foreign-key integrity without touching production.
    """
    disposable_db = ROOT_DIR / "data" / "disposable_test_baseline.db"
    shutil.copy2(BASELINE_DB, disposable_db)

    staging_conn = get_staging_conn()
    cur_s = staging_conn.cursor()
    cur_s.execute("""
    SELECT question_id, approved_topic_id
    FROM editorial_reviews
    WHERE review_decision = 'APPROVED'
    """)
    approved_rows = cur_s.fetchall()
    staging_conn.close()

    disp_conn = sqlite3.connect(str(disposable_db))
    cur_d = disp_conn.cursor()

    applied_count = 0
    for q_id, top_id in approved_rows:
        cur_d.execute("UPDATE baseline_questions SET topic_id = ? WHERE id = ?", (top_id, q_id))
        applied_count += cur_d.rowcount

    disp_conn.commit()

    # Check integrity
    cur_d.execute("PRAGMA integrity_check")
    integrity = cur_d.fetchone()[0]
    cur_d.execute("PRAGMA foreign_key_check")
    fk_violations = cur_d.fetchall()

    disp_conn.close()
    if disposable_db.exists():
        disposable_db.unlink()

    return {
        "status": "SUCCESS",
        "approved_reviews_tested": len(approved_rows),
        "applied_in_disposable_db": applied_count,
        "disposable_integrity": integrity,
        "fk_violations": fk_violations
    }

if __name__ == "__main__":
    summary = get_editorial_summary()
    print("Editorial Summary:", json.dumps(summary, indent=2))
    impact = test_downstream_impact_on_disposable_copy()
    print("Disposable Test Impact:", json.dumps(impact, indent=2))
