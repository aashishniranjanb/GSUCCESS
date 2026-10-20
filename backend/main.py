import os
import sys
import json
import sqlite3
import datetime
from datetime import timezone
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Depends, Security, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials, APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Ensure root directory modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from learner_engine import LearnerEngine
from vector_index import VectorIndexEngine
from knowledge_graph import KnowledgeGraphEngine
from backend.repositories import StudyRepository, SQLiteStudyRepository
from backend.evaluation import MockExamEngine, EvaluationRunner, BLUEPRINTS, MockBlueprint
from backend.observability import AdminObservabilityService
from backend.achievement_service import AchievementEngine
from backend.pilot_service import PilotService
from scripts.backup_db import create_backup, list_backups
from scripts.restore_db import verify_and_restore

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(Path(os.environ.get("GPAT_DB_PATH", os.environ.get("DB_PATH", ROOT_DIR / "gpat_knowledge.db"))).resolve())
BASELINE_DB_PATH = str(Path(os.environ.get("GPAT_BASELINE_DB_PATH", os.environ.get("BASELINE_DB_PATH", ROOT_DIR / "data" / "gpat_baseline.db"))).resolve())
MEDIA_DIR = ROOT_DIR / "baseline" / "media"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development").lower()
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "")

app = FastAPI(
    title="GPAT 2027 AI Learning OS API",
    version="1.1.0",
    description="Production-grade API for GPAT 2027 mobile PWA learning engine"
)

# CORS configuration
if ALLOWED_ORIGINS:
    origins = [orig.strip() for orig in ALLOWED_ORIGINS.split(",") if orig.strip()]
elif ENVIRONMENT == "production":
    origins = []
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security dependencies
security_basic = HTTPBasic(auto_error=False)
api_key_header = APIKeyHeader(name="X-Admin-Secret", auto_error=False)

def verify_admin_access(
    header_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPBasicCredentials] = Depends(security_basic)
) -> bool:
    """
    Validates admin access via Bearer/Header token or Basic Auth.
    Fails closed in production if ADMIN_SECRET is not configured.
    """
    admin_secret = os.environ.get("ADMIN_SECRET", ADMIN_SECRET).strip()
    if ENVIRONMENT == "production" and not admin_secret:
        raise HTTPException(
            status_code=500,
            detail="Admin access misconfigured: ADMIN_SECRET is required in production."
        )
    
    # In development, if no secret is set, provide a default warning pass or local token
    effective_secret = admin_secret or ("dev_secret" if ENVIRONMENT != "production" else "")
    if not effective_secret:
        raise HTTPException(status_code=401, detail="Unauthorized: No admin secret configured.")

    # 1. Check Header Key
    if header_key and header_key.strip() == effective_secret:
        return True

    # 2. Check HTTP Basic Auth (password must match secret)
    if credentials:
        if credentials.password == effective_secret or credentials.username == effective_secret:
            return True

    raise HTTPException(
        status_code=401,
        detail="Unauthorized: Valid admin credentials required.",
        headers={"WWW-Authenticate": "Basic"}
    )

# Lazy singletons
_repo: Optional[StudyRepository] = None
_learner_engine: Optional[LearnerEngine] = None
_vector_engine: Optional[VectorIndexEngine] = None
_kg_engine: Optional[KnowledgeGraphEngine] = None
_mock_engine: Optional[MockExamEngine] = None
_eval_runner: Optional[EvaluationRunner] = None
_admin_service: Optional[AdminObservabilityService] = None

def get_current_db_path() -> str:
    return str(Path(os.environ.get("GPAT_DB_PATH", os.environ.get("DB_PATH", ROOT_DIR / "gpat_knowledge.db"))).resolve())

def get_current_baseline_db_path() -> str:
    return str(Path(os.environ.get("GPAT_BASELINE_DB_PATH", os.environ.get("BASELINE_DB_PATH", ROOT_DIR / "data" / "gpat_baseline.db"))).resolve())

def get_admin_service() -> AdminObservabilityService:
    global _admin_service
    cur_db = get_current_db_path()
    if _admin_service is None or str(_admin_service.db_path) != cur_db:
        _admin_service = AdminObservabilityService(db_path=Path(cur_db))
    return _admin_service

def get_repo() -> StudyRepository:
    global _repo
    cur_db = get_current_db_path()
    if _repo is None or getattr(_repo, "db_path", None) != cur_db:
        _repo = SQLiteStudyRepository(db_path=cur_db)
    return _repo

def get_learner() -> LearnerEngine:
    global _learner_engine
    cur_db = get_current_db_path()
    if _learner_engine is None or getattr(_learner_engine, "db_path", None) != cur_db:
        _learner_engine = LearnerEngine(db_path=cur_db)
    return _learner_engine

def get_vector_engine() -> VectorIndexEngine:
    global _vector_engine
    cur_b_db = get_current_baseline_db_path()
    if _vector_engine is None or getattr(_vector_engine, "db_path", None) != cur_b_db:
        _vector_engine = VectorIndexEngine(db_path=cur_b_db)
    return _vector_engine

def get_kg_engine() -> KnowledgeGraphEngine:
    global _kg_engine
    cur_db = get_current_db_path()
    if _kg_engine is None or getattr(_kg_engine, "db_path", None) != cur_db:
        _kg_engine = KnowledgeGraphEngine(db_path=cur_db)
    return _kg_engine

def get_mock_engine() -> MockExamEngine:
    global _mock_engine
    cur_db = get_current_db_path()
    if _mock_engine is None or str(getattr(_mock_engine, "db_path", None)) != cur_db:
        _mock_engine = MockExamEngine(db_path=Path(cur_db))
    return _mock_engine

def get_eval_runner() -> EvaluationRunner:
    global _eval_runner
    if _eval_runner is None:
        _eval_runner = EvaluationRunner(db_path=Path(DB_PATH))
    return _eval_runner

_achievement_engine: Optional[AchievementEngine] = None
_pilot_service: Optional[PilotService] = None

def get_achievement_engine() -> AchievementEngine:
    global _achievement_engine
    cur_db = get_current_db_path()
    if _achievement_engine is None or getattr(_achievement_engine, "db_path", None) != cur_db:
        _achievement_engine = AchievementEngine(db_path=cur_db)
    return _achievement_engine

def get_pilot_service() -> PilotService:
    global _pilot_service
    cur_db = get_current_db_path()
    cur_base = get_current_baseline_db_path()
    if _pilot_service is None or getattr(_pilot_service, "db_path", None) != cur_db:
        _pilot_service = PilotService(db_path=cur_db, baseline_db_path=cur_base)
    return _pilot_service

# --- Request / Response Schemas ---

class AttemptSubmission(BaseModel):
    student_id: str = "student_01"
    question_id: str
    selected_option: int
    response_time_sec: float = 15.0
    confidence: int = 3
    hint_used: int = 0

class ReviewRatingSubmission(BaseModel):
    student_id: str = "student_01"
    card_id: Optional[int] = None
    question_id: str
    rating: str = Field(..., description="FSRS rating: Again, Hard, Good, or Easy")
    response_time_sec: float = 5.0

class QuestionOption(BaseModel):
    index: int
    text: str

class QuestionModel(BaseModel):
    id: str
    concept_id: str
    question_type: str
    difficulty: int
    question_text: str
    options: List[str]
    source_page: int
    cue: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: Optional[str] = None
    mission_id: Optional[str] = None
    session_time_minutes: int
    estimated_duration_minutes: Optional[int] = None
    target_question_count: int
    mode: Optional[str] = "balanced"
    status: Optional[str] = "active"
    headline: Optional[str] = "Build stronger recall."
    explanation: Optional[str] = "Review due concepts, repair weak areas, and establish baseline knowledge."
    why_this_mission: Optional[str] = "Prioritize eligible reviews and concepts needing more evidence."
    answered_count: Optional[int] = 0
    pending_count: Optional[int] = 0
    next_pending_index: Optional[int] = 0
    is_resumable: Optional[bool] = False
    is_completed: Optional[bool] = False
    composition: Optional[Dict[str, Any]] = None
    timeline: List[Dict[str, Any]]
    questions: List[Dict[str, Any]]

# --- API Routes ---

@app.get("/api/health")
def health_check():
    db_present = Path(DB_PATH).exists()
    return {
        "status": "healthy",
        "service": "gpat-ai-learning-os",
        "version": "1.1.0",
        "environment": ENVIRONMENT,
        "database_connected": db_present,
        "timestamp": datetime.datetime.now(timezone.utc).isoformat()
    }

class SyncAttemptItem(BaseModel):
    client_event_id: str
    student_id: str = "student_01"
    question_id: str
    selected_option: int
    response_time_sec: float = 15.0
    confidence: int = 3
    timestamp: str

class SyncBatchRequest(BaseModel):
    student_id: str = "student_01"
    events: List[SyncAttemptItem]

class MockCreateRequest(BaseModel):
    user_id: str = "student_01"
    blueprint_name: str = "sprint_25"
    custom_title: Optional[str] = None
    question_count: Optional[int] = None
    duration_minutes: Optional[int] = None
    topic_ids: Optional[List[str]] = None
    subject_ids: Optional[List[str]] = None

class MockAnswerRequest(BaseModel):
    user_id: str = "student_01"
    question_id: str
    selected_option: Optional[int] = None
    time_spent_ms: float = 0.0
    confidence: int = 3

class EvaluationRunRequest(BaseModel):
    version: str = "1.0.0"

class GoalUpdateRequest(BaseModel):
    student_id: str = "student_01"
    target_count: int = Field(5, ge=1, le=20)
    status: str = "active"
    goal_type: str = "completed_missions"

@app.get("/api/session", response_model=SessionResponse)
def get_daily_session(
    minutes: int = Query(12, ge=5, le=90),
    student_id: str = Query("student_01"),
    mode: str = Query("balanced", description="Learning mode: balanced, repair, review, exam"),
    engine: LearnerEngine = Depends(get_learner),
    repo: StudyRepository = Depends(get_repo)
):
    """
    Returns today's canonical session.
    If today's session was already generated, returns the persistent sequence.
    If not, generates it once, persists it to study_sessions, and logs SESSION_STARTED.
    """
    today_date = datetime.date.today().isoformat()
    existing = repo.get_or_create_daily_session(user_id=student_id, session_date=today_date, target_minutes=minutes)
    
    # If student explicitly chose a different duration (e.g. 5m vs 12m) and has answered 0 questions,
    # safely adjust session to match requested duration without losing progress:
    if existing and existing.get("status") != "completed":
        answered_items = [q for q in existing.get("questions", []) if q.get("item_status") == "answered"]
        if len(answered_items) == 0 and existing.get("session_time_minutes") != minutes:
            # Safe switch for unstarted mission
            new_session = engine.generate_daily_session(student_id=student_id, session_minutes=minutes, mode=mode)
            repo.persist_daily_session(
                user_id=student_id,
                session_date=today_date,
                target_minutes=minutes,
                questions=new_session["questions"]
            )
            existing = repo.get_or_create_daily_session(user_id=student_id, session_date=today_date, target_minutes=minutes)

    def synthesize_mission_ux(q_list, target_min, sess_status):
        total_q = len(q_list)
        answered = [q for q in q_list if q.get("item_status") == "answered"]
        pending = [q for q in q_list if q.get("item_status") != "answered"]
        answered_cnt = len(answered)
        pending_cnt = len(pending)
        next_idx = answered_cnt if pending_cnt > 0 else max(0, total_q - 1)
        is_completed = (sess_status == "completed") or (total_q > 0 and pending_cnt == 0)
        is_resumable = (not is_completed) and (answered_cnt > 0)

        # Count candidate categories
        due_cnt = sum(1 for q in q_list if q.get("candidate_type") == "DUE_REVIEW" or q.get("is_due"))
        repair_cnt = sum(1 for q in q_list if q.get("candidate_type") in ("TARGETED_REPAIR", "MISCONCEPTION_REPAIR") or q.get("has_active_misconception"))
        yield_cnt = total_q - due_cnt - repair_cnt

        # Calculate estimated duration (90s per question)
        est_sec = sum(q.get("estimated_seconds", 90) for q in q_list)
        est_min = max(1, round(est_sec / 60))

        # Dynamic evidence-grounded copy
        if due_cnt > 0 and repair_cnt > 0:
            headline = "Build stronger recall."
            explanation = "Review due concepts, repair weak areas, and test what you remember."
            why_text = f"Prioritizes {due_cnt} due reviews and {repair_cnt} active misconception traps."
        elif due_cnt > 0:
            headline = "Protect your retention."
            explanation = "Complete scheduled FSRS spaced reviews before memory decay accelerates."
            why_text = f"Prioritizes {due_cnt} due concepts requiring active recall reinforcement."
        elif repair_cnt > 0:
            headline = "Repair conceptual traps."
            explanation = "Untangle misconceptions where distractors were previously selected."
            why_text = f"Focuses on {repair_cnt} topics with confirmed distractor confusion."
        else:
            headline = "Establish your baseline."
            explanation = "Practice verified high-yield GPAT topics across the syllabus."
            why_text = "Balances high-yield exam weightage with active recall questions."

        return {
            "est_min": est_min,
            "headline": headline,
            "explanation": explanation,
            "why_text": why_text,
            "answered_cnt": answered_cnt,
            "pending_cnt": pending_cnt,
            "next_idx": next_idx,
            "is_resumable": is_resumable,
            "is_completed": is_completed,
            "due_cnt": due_cnt,
            "repair_cnt": repair_cnt,
            "yield_cnt": max(0, yield_cnt)
        }

    if existing:
        ux_meta = synthesize_mission_ux(existing["questions"], existing["session_time_minutes"], existing.get("status", "active"))
        return {
            "session_id": existing["session_id"],
            "mission_id": existing["session_id"],
            "session_time_minutes": existing["session_time_minutes"],
            "estimated_duration_minutes": ux_meta["est_min"],
            "target_question_count": existing["target_question_count"],
            "mode": mode,
            "status": existing.get("status", "active"),
            "headline": ux_meta["headline"],
            "explanation": ux_meta["explanation"],
            "why_this_mission": ux_meta["why_text"],
            "answered_count": ux_meta["answered_cnt"],
            "pending_count": ux_meta["pending_cnt"],
            "next_pending_index": ux_meta["next_idx"],
            "is_resumable": ux_meta["is_resumable"],
            "is_completed": ux_meta["is_completed"],
            "composition": {
                "due_recall_count": ux_meta["due_cnt"],
                "misconception_repair_count": ux_meta["repair_cnt"],
                "high_yield_concept_count": ux_meta["yield_cnt"]
            },
            "timeline": [
                {"block": "Due Recall & Retention", "duration_min": round(existing["session_time_minutes"] * 0.35, 1)},
                {"block": "Weakness & Misconception Repair", "duration_min": round(existing["session_time_minutes"] * 0.35, 1)},
                {"block": "High-Yield GPAT Application", "duration_min": round(existing["session_time_minutes"] * 0.30, 1)}
            ],
            "questions": existing["questions"]
        }
        
    # Generate new session using learning engine
    new_session = engine.generate_daily_session(student_id=student_id, session_minutes=minutes, mode=mode)
    
    # Persist canonically
    session_id = repo.persist_daily_session(
        user_id=student_id,
        session_date=today_date,
        target_minutes=minutes,
        questions=new_session["questions"]
    )
    new_session["session_id"] = session_id
    new_session["mission_id"] = session_id
    
    ux_meta = synthesize_mission_ux(new_session["questions"], minutes, "active")
    new_session["estimated_duration_minutes"] = ux_meta["est_min"]
    new_session["headline"] = ux_meta["headline"]
    new_session["explanation"] = ux_meta["explanation"]
    new_session["why_this_mission"] = ux_meta["why_text"]
    new_session["answered_count"] = 0
    new_session["pending_count"] = len(new_session["questions"])
    new_session["next_pending_index"] = 0
    new_session["is_resumable"] = False
    new_session["is_completed"] = False
    new_session["status"] = "active"

    # Log Session Started Event
    repo.log_learning_event(
        user_id=student_id,
        event_type="SESSION_STARTED",
        payload={"session_id": session_id, "session_date": today_date, "target_minutes": minutes, "mode": mode, "question_count": len(new_session["questions"])}
    )
    
    return new_session

@app.post("/api/attempt")
def record_attempt(
    attempt: AttemptSubmission,
    engine: LearnerEngine = Depends(get_learner),
    repo: StudyRepository = Depends(get_repo),
    ach_engine: Optional[AchievementEngine] = Depends(get_achievement_engine)
):
    if ach_engine is None or not hasattr(ach_engine, "evaluate_attempt_milestones"):
        ach_engine = get_achievement_engine()
    """Submits answer, updates FSRS card stability, catches misconceptions, records learning event, and updates session item."""
    try:
        feedback = engine.record_attempt(
            student_id=attempt.student_id,
            question_id=attempt.question_id,
            selected_option=attempt.selected_option,
            response_time_sec=attempt.response_time_sec,
            confidence=attempt.confidence
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Update persistent session item
    repo.update_session_item_result(
        user_id=attempt.student_id,
        question_id=attempt.question_id,
        is_correct=feedback["is_correct"]
    )
    
    # Log Learning Event with Calibration & Error Taxonomy
    repo.log_learning_event(
        user_id=attempt.student_id,
        event_type="QUESTION_ANSWERED",
        question_id=attempt.question_id,
        payload={
            "selected_option": attempt.selected_option,
            "is_correct": feedback["is_correct"],
            "response_time_sec": attempt.response_time_sec,
            "confidence": attempt.confidence,
            "calibration_category": feedback.get("calibration_category"),
            "error_type": feedback.get("error_type"),
            "fsrs_rating": feedback.get("fsrs_rating"),
            "stability_days": feedback.get("stability_days")
        }
    )
    
    if not feedback["is_correct"]:
        repo.log_learning_event(
            user_id=attempt.student_id,
            event_type="MISCONCEPTION_DETECTED",
            question_id=attempt.question_id,
            payload={
                "distractor_reason": feedback.get("distractor_reason"),
                "error_type": feedback.get("error_type"),
                "calibration": feedback.get("calibration_category")
            }
        )

    # Evaluate Learning-Based Milestones (Delayed Recall, Trap Repaired, Topic Mastery)
    new_achievements = ach_engine.evaluate_attempt_milestones(
        student_id=attempt.student_id,
        question_id=attempt.question_id,
        is_correct=feedback["is_correct"]
    )
    feedback["new_achievements"] = new_achievements
        
    return feedback

@app.post("/api/sync")
@app.post("/api/study/sync")
def sync_offline_attempts(
    batch: SyncBatchRequest,
    engine: LearnerEngine = Depends(get_learner),
    repo: StudyRepository = Depends(get_repo),
    ach_engine: Optional[AchievementEngine] = Depends(get_achievement_engine)
):
    if ach_engine is None or not hasattr(ach_engine, "evaluate_attempt_milestones"):
        ach_engine = get_achievement_engine()
    """
    Receives queued attempts stored in browser IndexedDB while offline.
    Uses SQLite transactions and durable uniqueness via synced_client_events table:
    - If client_event_id was already processed, returns 'duplicate' without re-applying FSRS or learning events.
    - If not processed, processes attempt, FSRS, session items, and learning events transactionally.
    - Handles partial batch failures: failed items are marked 'failed' and remain retryable.
    """
    results = []
    
    # Ensure synced_client_events table exists
    conn = sqlite3.connect(get_current_db_path())
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS synced_client_events (
        client_event_id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL,
        question_id TEXT NOT NULL,
        selected_option INTEGER NOT NULL,
        is_correct INTEGER NOT NULL,
        response_time_sec REAL,
        confidence INTEGER,
        processed_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

    for ev in batch.events:
        conn = sqlite3.connect(get_current_db_path(), timeout=10.0)
        cur = conn.cursor()
        try:
            # 1. Check for existing processed client event
            cur.execute("""
            SELECT is_correct, processed_at 
            FROM synced_client_events 
            WHERE client_event_id = ?
            """, (ev.client_event_id,))
            existing = cur.fetchone()

            if existing:
                results.append({
                    "client_event_id": ev.client_event_id,
                    "question_id": ev.question_id,
                    "status": "duplicate",
                    "is_correct": bool(existing[0]),
                    "processed_at": existing[1]
                })
                conn.close()
                continue

            # 2. Process attempt transactionally
            feedback = engine.record_attempt(
                student_id=batch.student_id,
                question_id=ev.question_id,
                selected_option=ev.selected_option,
                response_time_sec=ev.response_time_sec,
                confidence=ev.confidence,
                cur=cur
            )
            
            repo.update_session_item_result(
                user_id=batch.student_id,
                question_id=ev.question_id,
                is_correct=feedback["is_correct"],
                cur=cur
            )

            repo.log_learning_event(
                user_id=batch.student_id,
                event_type="OFFLINE_SYNC_ANSWERED",
                question_id=ev.question_id,
                payload={
                    "client_event_id": ev.client_event_id,
                    "timestamp": ev.timestamp,
                    "is_correct": feedback["is_correct"]
                },
                cur=cur
            )

            # 3. Record in synced_client_events to establish durable uniqueness
            now_iso = datetime.datetime.now(timezone.utc).isoformat()
            cur.execute("""
            INSERT INTO synced_client_events (
                client_event_id, student_id, question_id, selected_option,
                is_correct, response_time_sec, confidence, processed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ev.client_event_id,
                batch.student_id,
                ev.question_id,
                ev.selected_option,
                1 if feedback["is_correct"] else 0,
                ev.response_time_sec,
                ev.confidence,
                now_iso
            ))

            # 4. Evaluate achievements within same transaction
            ach_engine.evaluate_attempt_milestones(
                student_id=batch.student_id,
                question_id=ev.question_id,
                is_correct=feedback["is_correct"],
                cur=cur
            )

            conn.commit()

            results.append({
                "client_event_id": ev.client_event_id,
                "question_id": ev.question_id,
                "status": "synced",
                "is_correct": feedback["is_correct"]
            })
        except sqlite3.IntegrityError as ie:
            conn.rollback()
            # If concurrent request already inserted this client_event_id, fetch existing record
            try:
                cur.execute("SELECT is_correct, processed_at FROM synced_client_events WHERE client_event_id = ?", (ev.client_event_id,))
                row = cur.fetchone()
                if row:
                    results.append({
                        "client_event_id": ev.client_event_id,
                        "question_id": ev.question_id,
                        "status": "duplicate",
                        "is_correct": bool(row[0]),
                        "processed_at": row[1]
                    })
                else:
                    results.append({
                        "client_event_id": ev.client_event_id,
                        "question_id": ev.question_id,
                        "status": "failed",
                        "error": str(ie)
                    })
            except Exception:
                results.append({
                    "client_event_id": ev.client_event_id,
                    "question_id": ev.question_id,
                    "status": "duplicate",
                    "is_correct": True
                })
        except Exception as e:
            conn.rollback()
            results.append({
                "client_event_id": ev.client_event_id,
                "question_id": ev.question_id,
                "status": "failed",
                "error": str(e)
            })
        finally:
            conn.close()

    synced_or_dup_count = sum(1 for r in results if r["status"] in ("synced", "duplicate"))
    return {"synced_count": synced_or_dup_count, "results": results}


@app.get("/api/concepts")
def list_concepts():
    """Returns all high-yield concepts in the syllabus with domain, exam importance and objectives."""
    conn = sqlite3.connect(get_current_db_path())
    cur = conn.cursor()
    cur.execute("""
    SELECT id, name, domain_id, learning_objective, importance_score, difficulty
    FROM concepts
    ORDER BY importance_score DESC, difficulty ASC
    """)
    rows = [
        {
            "id": r[0],
            "name": r[1],
            "domain_id": r[2],
            "learning_objective": r[3],
            "importance_score": r[4],
            "difficulty": r[5]
        }
        for r in cur.fetchall()
    ]
    conn.close()
    return rows

# --- Canonical Syllabus Explorer & Content Library Endpoints ---

@app.get("/api/syllabus/tree")
def get_canonical_syllabus_tree():
    """
    Returns the complete 5-tier canonical syllabus tree:
    Level 1: Exam Group (5 areas per NBEMS)
    Level 2: Curriculum Subjects (19 academic courses per PCI)
    Level 3: Units / Chapters
    Level 4: Topics (221 topics with question/asset counts)
    Also returns active syllabus versions and curriculum stats.
    """
    db_path = get_current_baseline_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 0. Fetch active syllabus versions
    cur.execute("SELECT version_id, authority_name, title, effective_year, status FROM syllabus_versions WHERE status = 'ACTIVE' ORDER BY effective_year DESC")
    syllabus_versions = [dict(r) for r in cur.fetchall()]

    # 1. Fetch Exam Subjects (Level 1)
    cur.execute("SELECT subject_id, name, original_label FROM baseline_subjects ORDER BY subject_id")
    subjects = [dict(r) for r in cur.fetchall()]

    # 2. Fetch Curriculum Subjects (Level 2)
    cur.execute("""
    SELECT curriculum_subject_id, exam_subject_id, name, pci_course_code, semester_recommended, description
    FROM curriculum_subjects
    ORDER BY semester_recommended ASC, name ASC
    """)
    curr_subs = [dict(r) for r in cur.fetchall()]

    # 3. Fetch Units (Level 3)
    cur.execute("SELECT unit_id, curriculum_subject_id, unit_number, title FROM units ORDER BY unit_number ASC")
    units = [dict(r) for r in cur.fetchall()]
    units_by_curr = {}
    for u in units:
        units_by_curr.setdefault(u["curriculum_subject_id"], []).append(u)

    # 4. Fetch Topics with question and asset counts (Level 4)
    cur.execute("""
    SELECT t.topic_id, t.name, t.subject_id, t.curriculum_subject_id, t.unit_id,
           t.extraction_status, t.verification_status,
           count(DISTINCT q.id) as question_count,
           count(DISTINCT lo.objective_id) as objective_count,
           count(DISTINCT fc.card_id) as flashcard_count
    FROM baseline_topics t
    LEFT JOIN baseline_questions q ON t.topic_id = q.topic_id
    LEFT JOIN learning_objectives lo ON t.topic_id = lo.topic_id
    LEFT JOIN flashcards fc ON t.topic_id = fc.topic_id
    GROUP BY t.topic_id
    ORDER BY t.name ASC
    """)
    topics = [dict(r) for r in cur.fetchall()]
    conn.close()

    # Build nested tree structure
    topics_by_curr = {}
    total_verified_topics = 0
    total_needs_review_topics = 0

    for top in topics:
        c_id = top["curriculum_subject_id"] or top["unit_id"]
        is_verified = (top["verification_status"] == "VERIFIED")
        top["is_verified"] = is_verified
        if is_verified:
            total_verified_topics += 1
        else:
            total_needs_review_topics += 1
        topics_by_curr.setdefault(c_id, []).append(top)

    curr_by_exam = {}
    for cs in curr_subs:
        c_id = cs["curriculum_subject_id"]
        cs["topics"] = topics_by_curr.get(c_id, [])
        cs["units"] = units_by_curr.get(c_id, [])
        cs["unit_count"] = len(cs["units"])
        cs["topic_count"] = len(cs["topics"])
        cs["total_questions"] = sum(t["question_count"] for t in cs["topics"])
        curr_by_exam.setdefault(cs["exam_subject_id"], []).append(cs)

    tree = []
    for s in subjects:
        s_id = s["subject_id"]
        c_list = curr_by_exam.get(s_id, [])
        tree.append({
            "exam_subject_id": s_id,
            "name": s["name"],
            "curriculum_subjects": c_list,
            "curriculum_count": len(c_list),
            "total_topics": sum(c["topic_count"] for c in c_list),
            "total_questions": sum(c["total_questions"] for c in c_list)
        })

    return {
        "syllabus_versions": syllabus_versions,
        "total_exam_groups": len(tree),
        "total_curriculum_courses": len(curr_subs),
        "total_units": len(units),
        "total_topics": len(topics),
        "total_verified_topics": total_verified_topics,
        "total_needs_review_topics": total_needs_review_topics,
        "tree": tree
    }

@app.get("/api/syllabus/topic/{topic_id}")
def get_topic_detail(topic_id: str):
    """
    Returns full multimodal learning assets for a topic:
    - Topic metadata & curriculum placement (Level 1 Exam Area, Level 2 Course, Level 3 Unit)
    - Linked reference book chunks & page citations
    - Verified PYQs & practice questions
    - Active learning objectives (Level 5 Bloom's)
    - Flashcards
    - Available scientific figures and chemical structures with alt text and source metadata
    - Available content sources metadata
    """
    db_path = get_current_baseline_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
    SELECT t.topic_id, t.name, t.subject_id, t.curriculum_subject_id, t.unit_id,
           t.extraction_status, t.verification_status,
           cs.name as curriculum_name, cs.pci_course_code, cs.semester_recommended,
           bs.name as exam_subject_name,
           u.unit_number, u.title as unit_title
    FROM baseline_topics t
    LEFT JOIN curriculum_subjects cs ON t.curriculum_subject_id = cs.curriculum_subject_id
    LEFT JOIN baseline_subjects bs ON t.subject_id = bs.subject_id
    LEFT JOIN units u ON (t.unit_id = u.unit_id OR t.curriculum_subject_id = u.curriculum_subject_id)
    WHERE t.topic_id = ?
    """, (topic_id,))
    topic_row = cur.fetchone()
    if not topic_row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found.")

    # Fetch associated content chunks
    cur.execute("""
    SELECT chunk_id, source_id, page_or_range, heading_path, content, content_type
    FROM baseline_chunks
    WHERE topic_ids_json LIKE ?
    LIMIT 10
    """, (f'%"{topic_id}"%',))
    chunks = [dict(r) for r in cur.fetchall()]

    # Fetch associated questions with complete payload for practice player
    cur.execute("""
    SELECT q.id, q.pyq_year, q.question_text, q.difficulty, q.cognitive_level, q.verification_status,
           q.paper_id, q.media_id, q.options_json, q.correct_option, q.distractor_reasons_json,
           q.explanation, q.cue, q.source_page, q.provenance,
           m.relative_file_path as media_url, m.alt_text as media_alt, m.caption as media_caption
    FROM baseline_questions q
    LEFT JOIN baseline_media m ON q.media_id = m.media_id
    WHERE q.topic_id = ?
    LIMIT 20
    """, (topic_id,))
    raw_questions = [dict(r) for r in cur.fetchall()]
    questions = []
    for rq in raw_questions:
        try:
            rq["options"] = json.loads(rq.get("options_json") or "[]")
        except Exception:
            rq["options"] = []
        try:
            rq["distractor_reasons"] = json.loads(rq.get("distractor_reasons_json") or "{}")
        except Exception:
            rq["distractor_reasons"] = {}
        questions.append(rq)

    # Fetch associated learning objectives (Level 5)
    cur.execute("""
    SELECT objective_id, code, bloom_level, objective_statement, key_formula_or_rule, clinical_pearl
    FROM learning_objectives
    WHERE topic_id = ?
    """, (topic_id,))
    objectives = [dict(r) for r in cur.fetchall()]

    # Fetch associated flashcards
    cur.execute("""
    SELECT card_id, front, back, explanation, difficulty, importance
    FROM flashcards
    WHERE topic_id = ?
    """, (topic_id,))
    flashcards = [dict(r) for r in cur.fetchall()]

    # Fetch linked scientific figures, chemical structures, diagrams
    cur.execute("""
    SELECT DISTINCT m.media_id, m.media_type, m.relative_file_path, m.alt_text, m.caption,
           m.source_id, m.page_number, m.rights_status
    FROM baseline_media m
    JOIN baseline_questions q ON m.media_id = q.media_id
    WHERE q.topic_id = ?
    """, (topic_id,))
    media_items = [dict(r) for r in cur.fetchall()]

    # Fetch all registered baseline sources for provenance lookup
    cur.execute("""
    SELECT source_id, title, authority_category, conversion_tool, page_count_estimate
    FROM baseline_sources
    """)
    sources = [dict(r) for r in cur.fetchall()]

    conn.close()

    return {
        "topic": dict(topic_row),
        "content_chunks": chunks,
        "questions": questions,
        "learning_objectives": objectives,
        "flashcards": flashcards,
        "media": media_items,
        "sources": sources,
        "chunk_count": len(chunks),
        "question_count": len(questions),
        "objective_count": len(objectives),
        "flashcard_count": len(flashcards),
        "media_count": len(media_items)
    }

# --- Canonical PYQ Explorer & Practice Endpoints ---

@app.get("/api/pyqs/years")
def get_pyq_years():
    """
    Returns available verified PYQ exam years with question counts and official status.
    Excludes quarantined questions strictly.
    """
    db_path = get_current_baseline_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    SELECT pyq_year, count(*) as count
    FROM baseline_questions
    WHERE pyq_year IS NOT NULL AND quality_status = 'PUBLISHED'
    GROUP BY pyq_year
    ORDER BY pyq_year DESC
    """)
    rows = cur.fetchall()

    # Get quarantined counts per year from pyq_review_queue
    cur.execute("""
    SELECT pyq_year, count(*)
    FROM pyq_review_queue
    WHERE pyq_year IS NOT NULL
    GROUP BY pyq_year
    """)
    quarantine_map = dict(cur.fetchall())
    conn.close()

    return [
        {
            "year": r[0],
            "question_count": r[1],
            "quarantined_count": quarantine_map.get(r[0], 0),
            "status": "Official Key Verified" if r[0] >= 2020 else "Historical Key Verified",
            "paper_id": f"GPAT_{r[0]}"
        }
        for r in rows
    ]

@app.get("/api/pyqs/list")
def list_pyqs(
    year: Optional[int] = Query(None),
    subject_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=200)
):
    """
    Returns paginated published PYQs with strict exclusion of quarantined questions.
    Honors verification provenance and displays 'Topic mapping pending' where unmapped.
    """
    db_path = get_current_baseline_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    conditions = ["q.quality_status = 'PUBLISHED'", "q.pyq_year IS NOT NULL"]
    params: List[Any] = []

    if year is not None:
        conditions.append("q.pyq_year = ?")
        params.append(year)

    if subject_id:
        conditions.append("(t.subject_id = ? OR q.topic_id LIKE ?)")
        params.extend([subject_id, f"{subject_id}%"])

    if search:
        conditions.append("(q.question_text LIKE ? OR q.id LIKE ?)")
        search_pattern = f"%{search.strip()}%"
        params.extend([search_pattern, search_pattern])

    where_clause = " WHERE " + " AND ".join(conditions)

    # Count total
    count_sql = f"""
    SELECT count(*) 
    FROM baseline_questions q
    LEFT JOIN baseline_topics t ON q.topic_id = t.topic_id
    {where_clause}
    """
    cur.execute(count_sql, params)
    total_count = cur.fetchone()[0]

    # Select paginated
    offset = (page - 1) * page_size
    query_sql = f"""
    SELECT q.id, q.pyq_year, q.paper_id, q.question_type, q.cognitive_level,
           q.difficulty, q.question_text, q.options_json, q.cue,
           q.source_page, q.provenance, q.verification_status, q.answer_status,
           t.topic_id, t.name as topic_name, t.subject_id as topic_subject_id
    FROM baseline_questions q
    LEFT JOIN baseline_topics t ON q.topic_id = t.topic_id
    {where_clause}
    ORDER BY q.pyq_year DESC, q.id ASC
    LIMIT ? OFFSET ?
    """
    params.extend([page_size, offset])
    cur.execute(query_sql, params)
    
    questions = []
    for r in cur.fetchall():
        options = []
        if r["options_json"]:
            try:
                options = json.loads(r["options_json"])
            except Exception:
                options = []

        is_mapped = bool(r["topic_name"])
        topic_display = r["topic_name"] if is_mapped else "Topic mapping pending"

        # Determine subject display
        subj = r["topic_subject_id"]
        if not subj and r["topic_id"]:
            prefix = r["topic_id"].split("__")[0]
            if prefix in ("pharmacology", "pharmaceutics", "pharmaceutical_chemistry", "pharmacognosy", "other_subjects"):
                subj = prefix

        questions.append({
            "id": r["id"],
            "pyq_year": r["pyq_year"],
            "paper_id": r["paper_id"],
            "question_type": r["question_type"],
            "cognitive_level": r["cognitive_level"],
            "difficulty": r["difficulty"],
            "question_text": r["question_text"],
            "options": options,
            "cue": r["cue"],
            "source_page": r["source_page"],
            "provenance": r["provenance"],
            "verification_status": r["verification_status"],
            "answer_status": r["answer_status"],
            "topic_id": r["topic_id"],
            "topic_name": topic_display,
            "subject_id": subj,
            "is_mapped": is_mapped
        })

    conn.close()
    return {
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "questions": questions
    }

@app.get("/api/pyqs/{question_id}")
def get_pyq_detail(question_id: str):
    """
    Returns complete single PYQ item with verification status, options,
    answer provenance, distractor reasons, and eligible explanation.
    """
    db_path = get_current_baseline_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
    SELECT q.id, q.pyq_year, q.paper_id, q.question_type, q.cognitive_level,
           q.difficulty, q.question_text, q.options_json, q.correct_option,
           q.distractor_reasons_json, q.explanation, q.cue, q.source_page,
           q.provenance, q.verification_status, q.answer_status, q.quality_status,
           t.topic_id, t.name as topic_name, t.subject_id as topic_subject_id
    FROM baseline_questions q
    LEFT JOIN baseline_topics t ON q.topic_id = t.topic_id
    WHERE q.id = ? AND q.quality_status = 'PUBLISHED'
    """, (question_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Question {question_id} not found or quarantined.")

    options = []
    if row["options_json"]:
        try:
            options = json.loads(row["options_json"])
        except Exception:
            options = []

    distractor_reasons = {}
    if row["distractor_reasons_json"]:
        try:
            distractor_reasons = json.loads(row["distractor_reasons_json"])
        except Exception:
            distractor_reasons = {}

    is_mapped = bool(row["topic_name"])
    topic_display = row["topic_name"] if is_mapped else "Topic mapping pending"

    return {
        "id": row["id"],
        "pyq_year": row["pyq_year"],
        "paper_id": row["paper_id"],
        "question_type": row["question_type"],
        "cognitive_level": row["cognitive_level"],
        "difficulty": row["difficulty"],
        "question_text": row["question_text"],
        "options": options,
        "correct_option": row["correct_option"],
        "distractor_reasons": distractor_reasons,
        "explanation": row["explanation"],
        "cue": row["cue"],
        "source_page": row["source_page"],
        "provenance": row["provenance"],
        "verification_status": row["verification_status"],
        "answer_status": row["answer_status"],
        "topic_id": row["topic_id"],
        "topic_name": topic_display,
        "is_mapped": is_mapped
    }

@app.get("/api/progress")
def get_student_progress(student_id: str = Query("student_01")):
    """Calculates student memory matrix, retrievability, FSRS stability, and misconceptions."""
    conn = sqlite3.connect(get_current_db_path())
    cur = conn.cursor()
    cur.execute("""
    SELECT c.id, c.name, c.domain_id, c.importance_score,
           COALESCE(m.mastery, 0.0), COALESCE(m.stability, 0.0),
           COALESCE(m.retrievability, 1.0), COALESCE(m.attempts, 0),
           COALESCE(m.correct, 0), COALESCE(m.misconception_count, 0),
           m.last_review, m.next_review
    FROM concepts c
    LEFT JOIN concept_memory_state m ON c.id = m.concept_id AND m.student_id = ?
    ORDER BY c.importance_score DESC
    """, (student_id,))
    
    concepts_progress = []
    total_attempts = 0
    total_correct = 0
    mastered_count = 0
    misconception_count = 0

    for r in cur.fetchall():
        attempts = r[7]
        correct = r[8]
        mastery = r[4]
        misc = r[9]
        
        total_attempts += attempts
        total_correct += correct
        if mastery >= 0.75:
            mastered_count += 1
        misconception_count += misc

        # Gate 3 Deterministic Mastery State Transition Rules:
        # - UNASSESSED: No attempts
        # - NEEDS_REPAIR: Active/recurring misconceptions
        # - DEMONSTRATED_MASTERY: >=3 attempts, >=80% accuracy, stability >= 7 days
        # - RETAINING: stability >= 3 days, accuracy >= 60%
        # - LEARNING: In-progress (<3 attempts or stability < 3 days)
        if attempts == 0:
            m_state = "UNASSESSED"
        elif misc > 0:
            m_state = "NEEDS_REPAIR"
        elif attempts >= 3 and (correct / max(1, attempts)) >= 0.8 and r[5] >= 7.0:
            m_state = "DEMONSTRATED_MASTERY"
        elif r[5] >= 3.0 and (correct / max(1, attempts)) >= 0.6:
            m_state = "RETAINING"
        else:
            m_state = "LEARNING"

        concepts_progress.append({
            "id": r[0],
            "name": r[1],
            "domain_id": r[2],
            "importance_score": r[3],
            "mastery": mastery,
            "mastery_state": m_state,
            "stability_days": round(r[5], 2),
            "retrievability": r[6],
            "attempts": attempts,
            "correct": correct,
            "misconception_count": misc,
            "last_review": r[10],
            "next_review": r[11]
        })
        
    # Misconceptions breakdown
    cur.execute("""
    SELECT status, COUNT(*) FROM student_misconceptions
    WHERE student_id = ?
    GROUP BY status
    """, (student_id,))
    misc_status_counts = dict(cur.fetchall())
    
    # Active misconceptions list for Repair mode
    cur.execute("""
    SELECT m.id, m.concept_id, c.name as concept_name, m.question_id, m.distractor_reason, m.error_type, m.occurrence_count, m.status
    FROM student_misconceptions m
    JOIN concepts c ON m.concept_id = c.id
    WHERE m.student_id = ? AND m.status IN ('ACTIVE', 'RECURRING')
    ORDER BY m.occurrence_count DESC, m.last_detected DESC
    LIMIT 10
    """, (student_id,))
    active_traps = [
        {
            "id": row[0],
            "concept_id": row[1],
            "concept_name": row[2],
            "question_id": row[3],
            "distractor_reason": row[4],
            "error_type": row[5],
            "occurrence_count": row[6],
            "status": row[7]
        }
        for row in cur.fetchall()
    ]

    # Chronological Study Activity: attempts and missions aggregated by date
    cur.execute("""
    SELECT date(created_at) as study_date,
           COUNT(*) as total_attempts,
           SUM(is_correct) as correct_attempts,
           AVG(response_time_sec) as avg_time_sec
    FROM student_attempts
    WHERE student_id = ?
    GROUP BY date(created_at)
    ORDER BY study_date ASC
    """, (student_id,))
    daily_activity = [
        {
            "date": row[0],
            "attempts": row[1],
            "correct": row[2] or 0,
            "incorrect": row[1] - (row[2] or 0),
            "accuracy_percent": round(((row[2] or 0) / max(1, row[1])) * 100, 1),
            "avg_time_sec": round(row[3] or 0.0, 1)
        }
        for row in cur.fetchall()
    ]

    # FSRS Review Workload metrics
    now_iso = datetime.datetime.now(timezone.utc).isoformat()
    cur.execute("""
    SELECT COUNT(*) FROM fsrs_cards
    WHERE student_id = ? AND due <= ?
    """, (student_id, now_iso))
    due_reviews_count = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*) FROM fsrs_cards
    WHERE student_id = ?
    """, (student_id,))
    total_cards_count = cur.fetchone()[0]

    cur.execute("""
    SELECT state, COUNT(*) FROM fsrs_cards
    WHERE student_id = ?
    GROUP BY state
    """, (student_id,))
    cards_by_state = dict(cur.fetchall())

    # Completed study sessions count
    cur.execute("""
    SELECT COUNT(*), MAX(completed_at) FROM study_sessions
    WHERE user_id = ? AND status = 'completed'
    """, (student_id,))
    sess_row = cur.fetchone()
    completed_sessions = sess_row[0] if sess_row else 0
    latest_completed_session = sess_row[1] if sess_row else None

    # Latest activity timestamp
    cur.execute("""
    SELECT MAX(created_at) FROM student_attempts WHERE student_id = ?
    """, (student_id,))
    latest_attempt_date = cur.fetchone()[0]

    # Domain performance breakdown from verified concept mappings
    cur.execute("""
    SELECT c.domain_id,
           COUNT(a.id) as attempts,
           SUM(a.is_correct) as correct
    FROM student_attempts a
    JOIN concepts c ON a.concept_id = c.id
    WHERE a.student_id = ?
    GROUP BY c.domain_id
    """, (student_id,))
    domain_performance = [
        {
            "domain_id": row[0],
            "attempts": row[1],
            "correct": row[2] or 0,
            "incorrect": row[1] - (row[2] or 0),
            "accuracy_percent": round(((row[2] or 0) / max(1, row[1])) * 100, 1)
        }
        for row in cur.fetchall()
    ]

    # Syllabus coverage breakdown across all subjects and domains
    cur.execute("""
    SELECT c.domain_id,
           COUNT(DISTINCT c.id) as total_concepts,
           COUNT(DISTINCT CASE WHEN a.id IS NOT NULL THEN c.id END) as assessed_concepts,
           COUNT(a.id) as total_attempts,
           SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) as correct_attempts
    FROM concepts c
    LEFT JOIN student_attempts a ON c.id = a.concept_id AND a.student_id = ?
    GROUP BY c.domain_id
    ORDER BY c.domain_id ASC
    """, (student_id,))
    syllabus_coverage = [
        {
            "domain_id": row[0],
            "total_concepts": row[1],
            "assessed_concepts": row[2],
            "unassessed_concepts": row[1] - row[2],
            "coverage_percent": round((row[2] / max(1, row[1])) * 100, 1),
            "attempts": row[3],
            "correct": row[4] or 0
        }
        for row in cur.fetchall()
    ]

    # FSRS review forecast (overdue, due today, next 3 days, next 7 days, next 14 days)
    now_dt = datetime.datetime.now(timezone.utc)
    now_iso = now_dt.isoformat()
    overdue_cutoff_iso = (now_dt - datetime.timedelta(days=1)).isoformat()
    three_days_iso = (now_dt + datetime.timedelta(days=3)).isoformat()
    seven_days_iso = (now_dt + datetime.timedelta(days=7)).isoformat()
    fourteen_days_iso = (now_dt + datetime.timedelta(days=14)).isoformat()

    cur.execute("""
    SELECT COUNT(*) FROM fsrs_cards
    WHERE student_id = ? AND due < ?
    """, (student_id, overdue_cutoff_iso))
    overdue_reviews_count = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*) FROM fsrs_cards
    WHERE student_id = ? AND due > ? AND due <= ?
    """, (student_id, now_iso, three_days_iso))
    due_in_3_days_count = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*) FROM fsrs_cards
    WHERE student_id = ? AND due > ? AND due <= ?
    """, (student_id, now_iso, seven_days_iso))
    due_in_7_days_count = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*) FROM fsrs_cards
    WHERE student_id = ? AND due > ? AND due <= ?
    """, (student_id, now_iso, fourteen_days_iso))
    due_in_14_days_count = cur.fetchone()[0]

    # Evaluated Mini Mocks / Mocks taken by this student
    cur.execute("""
    SELECT id, title, blueprint_name, total_questions, score, score_percent, accuracy_percent, submitted_at, result_json
    FROM mock_exams
    WHERE user_id = ? AND status = 'EVALUATED'
    ORDER BY submitted_at DESC
    LIMIT 10
    """, (student_id,))
    mock_history = []
    for m_row in cur.fetchall():
        parsed_result = None
        if m_row[8]:
            try:
                parsed_result = json.loads(m_row[8])
            except Exception:
                parsed_result = None

        mock_history.append({
            "id": m_row[0],
            "title": m_row[1],
            "blueprint_name": m_row[2],
            "total_questions": m_row[3],
            "score": m_row[4],
            "score_percent": m_row[5],
            "accuracy_percent": m_row[6],
            "submitted_at": m_row[7],
            "result": parsed_result
        })

    # Find weak demonstrated concepts for recommendation (attempts >= 1, accuracy < 60%)
    cur.execute("""
    SELECT m.concept_id, c.name, m.attempts, m.correct, (CAST(m.correct AS FLOAT) / max(1, m.attempts)) as acc
    FROM concept_memory_state m
    JOIN concepts c ON m.concept_id = c.id
    WHERE m.student_id = ? AND m.attempts >= 1
    ORDER BY acc ASC, m.attempts DESC
    LIMIT 1
    """, (student_id,))
    weak_concept_row = cur.fetchone()

    # Find high-yield unassessed concept with available questions
    cur.execute("""
    SELECT c.id, c.name, c.domain_id, c.importance_score, COUNT(q.id) as q_count
    FROM concepts c
    JOIN questions q ON c.id = q.concept_id
    LEFT JOIN student_attempts a ON c.id = a.concept_id AND a.student_id = ?
    WHERE a.id IS NULL
    GROUP BY c.id
    ORDER BY c.importance_score DESC, q_count DESC
    LIMIT 1
    """, (student_id,))
    unassessed_row = cur.fetchone()

    conn.close()
    
    overall_accuracy = round(total_correct / max(1, total_attempts) * 100, 1)

    # Calculate authoritative streak: consecutive days with at least 1 study event
    active_dates = {d["date"] for d in daily_activity}
    streak_days = len(active_dates) # Documented as verified active study days count

    # Authoritative 5-Level Recommendation Hierarchy (Task 3 specification):
    # 1. Overdue / Due FSRS reviews
    # 2. Repeated misconceptions and high-confidence errors
    # 3. Topics with weak demonstrated performance (<60% accuracy)
    # 4. Important unassessed syllabus areas with eligible questions
    # 5. Mixed practice or daily mission fallback
    if due_reviews_count > 0:
        recommended_action = {
            "type": "review",
            "title": f"Review {due_reviews_count} Due Flashcards",
            "description": f"FSRS intervals indicate memory decay on {due_reviews_count} active cards. Review immediately to stabilize long-term retention.",
            "cta_label": "Start Flashcard Review",
            "cta_href": "/review",
            "rationale": "High priority: FSRS scheduled interval has elapsed, risk of forgetting is elevated."
        }
    elif active_traps:
        trap = active_traps[0]
        recommended_action = {
            "type": "repair",
            "title": f"Repair: {trap['concept_name']}",
            "description": f"Repeated misconception detected ({trap['error_type']}). Caught {trap['occurrence_count']} time(s). Clear cognitive trap with high-yield drills.",
            "cta_label": "Begin Targeted Repair",
            "cta_href": f"/today?mode=repair&concept={trap['concept_id']}",
            "rationale": "Second priority: Identified distractor trap will cause repeated negative marks (-1 NBEMS penalty) if unaddressed."
        }
    elif weak_concept_row and weak_concept_row[4] < 0.6:
        w_id, w_name, w_att, w_corr, w_acc = weak_concept_row
        recommended_action = {
            "type": "practice",
            "title": f"Strengthen: {w_name}",
            "description": f"Demonstrated accuracy is only {round(w_acc * 100)}% ({w_corr}/{w_att} correct). Focused question practice will reinforce foundational principles.",
            "cta_label": f"Practice {w_name}",
            "cta_href": f"/learn?topic={w_id}",
            "rationale": "Third priority: Assessed performance on this concept is below 60% mastery threshold."
        }
    elif unassessed_row:
        u_id, u_name, u_domain, u_imp, u_qcount = unassessed_row
        recommended_action = {
            "type": "explore",
            "title": f"Explore Unassessed Area: {u_name}",
            "description": f"High-yield concept in {u_domain.replace('_', ' ')} with {u_qcount} eligible practice questions. Test your baseline knowledge.",
            "cta_label": f"Explore {u_name}",
            "cta_href": f"/learn?topic={u_id}",
            "rationale": "Fourth priority: High-importance syllabus topic with zero recorded assessments."
        }
    else:
        recommended_action = {
            "type": "mission",
            "title": "Complete Daily Study Mission",
            "description": "All scheduled reviews and active traps are clear. Continue steady preparation with today's 12-minute mission.",
            "cta_label": "Start Today's Mission",
            "cta_href": "/today",
            "rationale": "Fifth priority: Balanced daily mission to maintain steady progress across disciplines."
        }

    return {
        "student_id": student_id,
        "summary": {
            "total_concepts": len(concepts_progress),
            "mastered_concepts": mastered_count,
            "total_attempts": total_attempts,
            "total_correct": total_correct,
            "total_incorrect": total_attempts - total_correct,
            "overall_accuracy_percent": overall_accuracy,
            "completed_sessions": completed_sessions,
            "latest_activity_date": latest_attempt_date or latest_completed_session,
            "active_misconceptions": misc_status_counts.get("ACTIVE", 0) + misc_status_counts.get("RECURRING", 0),
            "repaired_misconceptions": misc_status_counts.get("REPAIRED", 0),
            "recurring_misconceptions": misc_status_counts.get("RECURRING", 0),
            "active_study_days": streak_days,
            "status": "Active Learner" if total_attempts > 0 else "Unassessed"
        },
        "daily_activity": daily_activity,
        "fsrs_workload": {
            "due_reviews": due_reviews_count,
            "overdue_reviews": overdue_reviews_count,
            "total_cards": total_cards_count,
            "learning_cards": cards_by_state.get(1, 0),
            "review_cards": cards_by_state.get(2, 0),
            "forecast_3_days": due_in_3_days_count,
            "forecast_7_days": due_in_7_days_count,
            "forecast_14_days": due_in_14_days_count
        },
        "domain_performance": domain_performance,
        "syllabus_coverage": syllabus_coverage,
        "active_traps": active_traps,
        "recommended_next_action": recommended_action,
        "mock_history": mock_history,
        "concepts": concepts_progress
    }

# ============================================================================
# Phase 3: Personalized Study Orchestration Endpoints
# ============================================================================

@app.get("/api/study/today")
def get_study_today(
    minutes: int = Query(12, ge=5, le=90),
    student_id: str = Query("student_01"),
    mode: str = Query("balanced"),
    engine: LearnerEngine = Depends(get_learner),
    repo: StudyRepository = Depends(get_repo)
):
    """
    Returns today's active study mission and learner state.
    Guarantees deterministic, idempotent mission generation and persistence.
    """
    return get_daily_session(minutes=minutes, student_id=student_id, mode=mode, engine=engine, repo=repo)

@app.post("/api/study/mission")
def create_study_mission(
    minutes: int = Query(12, ge=5, le=90),
    student_id: str = Query("student_01"),
    mode: str = Query("balanced"),
    force_regenerate: bool = Query(False),
    engine: LearnerEngine = Depends(get_learner),
    repo: StudyRepository = Depends(get_repo)
):
    """Explicitly generates or retrieves a personalized study mission."""
    today_date = datetime.date.today().isoformat()
    if not force_regenerate:
        existing = repo.get_or_create_daily_session(user_id=student_id, session_date=today_date, target_minutes=minutes)
        if existing:
            return existing

    new_session = engine.generate_daily_session(student_id=student_id, session_minutes=minutes, mode=mode)
    session_id = repo.persist_daily_session(
        user_id=student_id,
        session_date=today_date,
        target_minutes=minutes,
        questions=new_session["questions"]
    )
    new_session["session_id"] = session_id
    new_session["mission_id"] = session_id
    repo.log_learning_event(
        user_id=student_id,
        event_type="MISSION_CREATED",
        payload={"session_id": session_id, "session_date": today_date, "target_minutes": minutes, "mode": mode, "task_count": len(new_session["questions"])}
    )
    return new_session

@app.get("/api/study/mission/{mission_id}")
def get_mission_by_id(
    mission_id: str,
    repo: StudyRepository = Depends(get_repo)
):
    """Retrieves a specific study mission by ID."""
    conn = sqlite3.connect(get_current_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT user_id, session_date, target_minutes FROM study_sessions WHERE id = ?", (mission_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Mission not found.")
    mission = repo.get_or_create_daily_session(user_id=row["user_id"], session_date=row["session_date"], target_minutes=row["target_minutes"])
    return mission

@app.post("/api/study/attempt")
def submit_study_attempt(
    attempt: AttemptSubmission,
    engine: LearnerEngine = Depends(get_learner),
    repo: StudyRepository = Depends(get_repo)
):
    """Submits answer through the authoritative result processor."""
    return record_attempt(attempt=attempt, engine=engine, repo=repo)

@app.get("/api/study/review-queue")
def get_study_review_queue(
    student_id: str = Query("student_01"),
    engine: LearnerEngine = Depends(get_learner)
):
    """Returns all FSRS cards currently due for review."""
    conn = sqlite3.connect(get_current_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    now_iso = datetime.datetime.now(timezone.utc).isoformat()
    cur.execute("""
    SELECT c.card_id, c.item_id, q.concept_id, c.due, c.stability, c.difficulty, c.step, c.state,
           q.question_text, q.options_json, q.cue, q.explanation, q.correct_option, co.name as concept_name
    FROM fsrs_cards c
    JOIN questions q ON c.item_id = q.id
    LEFT JOIN concepts co ON q.concept_id = co.id
    WHERE c.student_id = ? AND c.item_type = 'question' AND c.due <= ?
    ORDER BY c.due ASC
    """, (student_id, now_iso))
    due_items = []
    for r in cur.fetchall():
        opts = []
        if r["options_json"]:
            try:
                opts = json.loads(r["options_json"])
            except Exception:
                opts = []

        due_items.append({
            "card_id": r["card_id"],
            "question_id": r["item_id"],
            "concept_id": r["concept_id"],
            "concept_name": r["concept_name"] or "Pharmacology Concept",
            "due": r["due"],
            "stability_days": round(r["stability"], 2),
            "step": r["step"],
            "state": r["state"],
            "question_text": r["question_text"],
            "options": opts,
            "correct_option": r["correct_option"],
            "explanation": r["explanation"],
            "cue": r["cue"]
        })
    conn.close()
    return {"student_id": student_id, "due_count": len(due_items), "review_items": due_items}

@app.post("/api/study/review-rating")
def submit_study_review_rating(
    sub: ReviewRatingSubmission,
    engine: LearnerEngine = Depends(get_learner),
    repo: StudyRepository = Depends(get_repo)
):
    """
    Directly updates FSRS card stability and difficulty based on user's self-assessed rating
    (Again, Hard, Good, Easy) using the authoritative FSRS scheduler.
    """
    import fsrs
    rating_map = {
        "again": fsrs.Rating.Again,
        "hard": fsrs.Rating.Hard,
        "good": fsrs.Rating.Good,
        "easy": fsrs.Rating.Easy,
    }

    norm_rating = sub.rating.strip().lower()
    if norm_rating not in rating_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid rating '{sub.rating}'. Must be one of: Again, Hard, Good, Easy."
        )

    fsrs_enum = rating_map[norm_rating]

    conn = sqlite3.connect(get_current_db_path())
    cur = conn.cursor()

    try:
        # Check question exists
        cur.execute("SELECT concept_id, question_text, explanation FROM questions WHERE id = ?", (sub.question_id,))
        q_row = cur.fetchone()
        if not q_row:
            raise HTTPException(status_code=404, detail=f"Question {sub.question_id} not found in learner database.")

        concept_id = q_row[0]

        # Get or create FSRS card
        card = engine.get_or_create_fsrs_card(sub.student_id, sub.question_id, item_type="question", cur=cur)

        # Review card through backend FSRS scheduler
        updated_card, review_log = engine.scheduler.review_card(card, fsrs_enum)

        # Update card in database
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

        # Log learning event
        repo.log_learning_event(
            user_id=sub.student_id,
            event_type="CARD_REVIEWED",
            question_id=sub.question_id,
            payload={
                "rating": sub.rating,
                "stability_days": round(updated_card.stability, 2),
                "difficulty": round(updated_card.difficulty, 2),
                "due": updated_card.due.isoformat(),
                "response_time_sec": sub.response_time_sec
            },
            cur=cur
        )

        conn.commit()

        return {
            "status": "success",
            "card_id": updated_card.card_id,
            "question_id": sub.question_id,
            "rating": sub.rating,
            "state": updated_card.state.value,
            "stability_days": round(updated_card.stability, 2),
            "difficulty": round(updated_card.difficulty, 2),
            "due": updated_card.due.isoformat(),
            "explanation": q_row[2]
        }
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/study/progress")
def get_study_progress(
    student_id: str = Query("student_01")
):
    """Returns learner progress with explicit separation of unassessed concepts."""
    return get_student_progress(student_id=student_id)

@app.post("/api/study/mission/{mission_id}/complete")
def complete_study_mission(
    mission_id: str,
    repo: StudyRepository = Depends(get_repo),
    ach_engine: Optional[AchievementEngine] = Depends(get_achievement_engine)
):
    if ach_engine is None or not hasattr(ach_engine, "evaluate_mission_completion"):
        ach_engine = get_achievement_engine()
    """Marks an active mission as completed once all tasks are answered."""
    conn = sqlite3.connect(get_current_db_path())
    cur = conn.cursor()
    now_iso = datetime.datetime.now(timezone.utc).isoformat()
    cur.execute("UPDATE study_sessions SET status = 'completed', completed_at = ? WHERE id = ?", (now_iso, mission_id))
    cur.execute("SELECT user_id FROM study_sessions WHERE id = ?", (mission_id,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    
    new_achievements = []
    if row:
        user_id = row[0]
        repo.log_learning_event(
            user_id=user_id,
            event_type="MISSION_COMPLETED",
            payload={"mission_id": mission_id, "completed_at": now_iso}
        )
        new_achievements = ach_engine.evaluate_mission_completion(student_id=user_id, session_id=mission_id)
        
    return {"status": "success", "mission_id": mission_id, "completed_at": now_iso, "new_achievements": new_achievements}

# ============================================================================
# Progress Rewards & Learning Milestones Endpoints
# ============================================================================

@app.get("/api/rewards")
def get_learner_rewards(
    student_id: str = Query("student_01"),
    ach_engine: AchievementEngine = Depends(get_achievement_engine)
):
    """Returns the student's earned learning milestones, weekly study goals, and personal bests."""
    return ach_engine.get_progress_rewards(student_id=student_id)

@app.post("/api/rewards/goal")
def set_learner_goal(
    req: GoalUpdateRequest,
    ach_engine: AchievementEngine = Depends(get_achievement_engine)
):
    """Configures a flexible, non-punitive weekly study goal without resetting history or progress."""
    updated = ach_engine.update_goal(
        student_id=req.student_id,
        target_count=req.target_count,
        status=req.status,
        goal_type=req.goal_type
    )
    return {"status": "success", "goal": updated}

@app.get("/api/search")
def search_tutor(
    q: str = Query(..., min_length=2),
    v_engine: VectorIndexEngine = Depends(get_vector_engine)
):
    """Hybrid RRF Search returning verified textbook passages and strictly PUBLISHED claims with exact page citations."""
    blocks = v_engine.hybrid_search(q, top_k=5)
    
    conn = sqlite3.connect(get_current_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    enriched_blocks = []
    for b in blocks:
        b_id = b["block_id"]
        # Only attach claims that have passed the ClaimVerifier and are PUBLISHED
        cur.execute("""
        SELECT id, concept_id, page_number, claim_text, confidence, verification_status
        FROM candidate_claims
        WHERE source_block_id = ? AND verification_status = 'PUBLISHED'
        """, (b_id,))
        published_claims = [
            {
                "claim_id": row["id"],
                "concept_id": row["concept_id"],
                "page": row["page_number"],
                "claim": row["claim_text"],
                "confidence": row["confidence"],
                "status": row["verification_status"]
            }
            for row in cur.fetchall()
        ]
        
        b_copy = dict(b)
        b_copy["published_claims"] = published_claims
        enriched_blocks.append(b_copy)
        
    conn.close()
    return {"query": q, "blocks": enriched_blocks}

@app.get("/api/graph_reason")
def graph_reason(
    start: str = Query(..., description="Start entity or drug"),
    end: str = Query(..., description="End entity, receptor, or disease"),
    k_engine: KnowledgeGraphEngine = Depends(get_kg_engine)
):
    """Traverses multi-hop relational pathway and builds a Section 11 Evidence Contract."""
    contract = k_engine.generate_evidence_contract(
        f"Mechanistic pathway connecting {start} and {end}", start, end
    )
    return contract

@app.get("/api/library")
def get_library_documents():
    """Returns ingested source textbooks, chapter ranges, authority levels and chunk counts."""
    conn = sqlite3.connect(get_current_db_path())
    cur = conn.cursor()
    cur.execute("SELECT id, filename, title, authority_level, total_pages, status FROM documents")
    docs = []
    for r in cur.fetchall():
        cur.execute("SELECT COUNT(*) FROM content_blocks WHERE document_id = ?", (r[0],))
        b_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM candidate_claims WHERE source_block_id IN (SELECT id FROM content_blocks WHERE document_id = ?)", (r[0],))
        c_count = cur.fetchone()[0]
        
        docs.append({
            "id": r[0],
            "filename": r[1],
            "title": r[2],
            "authority_level": r[3],
            "total_pages": r[4],
            "status": r[5],
            "blocks_ingested": b_count,
            "claims_extracted": c_count
        })
    conn.close()
    return {"documents": docs}

# --- Mock Exam Simulation Endpoints ---

@app.get("/api/mock/blueprints")
def list_mock_blueprints():
    """Returns available mock exam blueprints with authoritative question count, duration, and marking."""
    return {
        "blueprints": [
            {
                "id": "sprint_25",
                "name": BLUEPRINTS["sprint_25"].name,
                "title": BLUEPRINTS["sprint_25"].title,
                "exam_version": BLUEPRINTS["sprint_25"].exam_version,
                "total_questions": BLUEPRINTS["sprint_25"].total_questions,
                "duration_minutes": BLUEPRINTS["sprint_25"].duration_minutes,
                "duration_seconds": BLUEPRINTS["sprint_25"].duration_minutes * 60,
                "marks_per_question": BLUEPRINTS["sprint_25"].marks_per_question,
                "negative_marks": BLUEPRINTS["sprint_25"].negative_marks,
                "difficulty_distribution": BLUEPRINTS["sprint_25"].difficulty_distribution,
                "description": "Fast 25-question high-yield sprint for targeted assessment."
            },
            {
                "id": "full_40",
                "name": BLUEPRINTS["full_40"].name,
                "title": BLUEPRINTS["full_40"].title,
                "exam_version": BLUEPRINTS["full_40"].exam_version,
                "total_questions": BLUEPRINTS["full_40"].total_questions,
                "duration_minutes": BLUEPRINTS["full_40"].duration_minutes,
                "duration_seconds": BLUEPRINTS["full_40"].duration_minutes * 60,
                "marks_per_question": BLUEPRINTS["full_40"].marks_per_question,
                "negative_marks": BLUEPRINTS["full_40"].negative_marks,
                "difficulty_distribution": BLUEPRINTS["full_40"].difficulty_distribution,
                "description": "Comprehensive 40-question sectional pharmacology mock."
            },
            {
                "id": "mini_mock",
                "name": "PERSONALIZED_MINI_MOCK",
                "title": "Personalized Mini Mock (Custom Syllabus Scope)",
                "exam_version": "PROVISIONAL_MOCK",
                "total_questions": 10,
                "duration_minutes": 18,
                "duration_seconds": 18 * 60,
                "marks_per_question": 4.0,
                "negative_marks": 1.0,
                "difficulty_distribution": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
                "description": "Customizable 5 to 50 question mini mock scoped to your chosen subjects, units, or topics."
            },
            {
                "id": "official_125",
                "name": BLUEPRINTS["official_125"].name,
                "title": BLUEPRINTS["official_125"].title,
                "exam_version": BLUEPRINTS["official_125"].exam_version,
                "total_questions": BLUEPRINTS["official_125"].total_questions,
                "duration_minutes": BLUEPRINTS["official_125"].duration_minutes,
                "duration_seconds": BLUEPRINTS["official_125"].duration_minutes * 60,
                "marks_per_question": BLUEPRINTS["official_125"].marks_per_question,
                "negative_marks": BLUEPRINTS["official_125"].negative_marks,
                "difficulty_distribution": BLUEPRINTS["official_125"].difficulty_distribution,
                "description": "Full-length 125-question GPAT simulation following NBEMS standard pattern."
            }
        ]
    }

@app.post("/api/mock/create")
def create_mock(
    req: MockCreateRequest,
    engine: MockExamEngine = Depends(get_mock_engine)
):
    """Creates a new mock exam session with controlled unskewed blueprint constraints."""
    if req.topic_ids or req.question_count or req.blueprint_name == "mini_mock":
        q_count = max(5, min(req.question_count or 10, 50))
        duration = req.duration_minutes or round(q_count * 1.8)
        title = req.custom_title or f"Personalized Mini Mock ({q_count} Questions)"
        custom_bp = MockBlueprint(
            name="PERSONALIZED_MINI_MOCK",
            exam_version="PROVISIONAL_MOCK",
            title=title,
            total_questions=q_count,
            duration_minutes=duration,
            marks_per_question=4.0,
            negative_marks=1.0,
            selected_topic_ids=req.topic_ids,
            selected_subject_ids=req.subject_ids
        )
        return engine.create_mock_exam(
            user_id=req.user_id,
            blueprint_name="mini_mock",
            custom_blueprint=custom_bp
        )

    return engine.create_mock_exam(user_id=req.user_id, blueprint_name=req.blueprint_name)

class MiniMockCoverageRequest(BaseModel):
    topic_ids: Optional[List[str]] = None
    subject_ids: Optional[List[str]] = None
    requested_count: int = 10

@app.post("/api/mock/mini-mock-coverage")
def get_mini_mock_coverage(
    req: MiniMockCoverageRequest,
    engine: MockExamEngine = Depends(get_mock_engine)
):
    """
    Analyzes selectable topics/concepts and returns real eligible question counts,
    distribution per concept, and coverage warnings without creating an exam.
    """
    conn = engine._get_connection()
    cur = conn.cursor()

    query = """
    SELECT q.id, q.concept_id, c.name as concept_name, c.domain_id, q.difficulty
    FROM questions q
    JOIN concepts c ON q.concept_id = c.id
    """
    params: List[Any] = []
    conditions = []

    if req.topic_ids:
        placeholders = ",".join("?" for _ in req.topic_ids)
        conditions.append(f"(q.concept_id IN ({placeholders}) OR c.domain_id IN ({placeholders}))")
        params.extend(req.topic_ids)
        params.extend(req.topic_ids)

    if req.subject_ids:
        placeholders = ",".join("?" for _ in req.subject_ids)
        conditions.append(f"c.domain_id IN ({placeholders})")
        params.extend(req.subject_ids)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY q.id ASC"
    cur.execute(query, tuple(params))
    rows = [dict(r) for r in cur.fetchall()]

    # Fetch all available domains and concepts with question counts for builder navigation
    cur.execute("""
    SELECT c.domain_id, c.id as concept_id, c.name as concept_name, count(q.id) as question_count
    FROM concepts c
    LEFT JOIN questions q ON q.concept_id = c.id
    GROUP BY c.id
    ORDER BY c.domain_id, c.name
    """)
    all_concept_rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    # Group concepts into domains
    domain_map: Dict[str, Dict[str, Any]] = {}
    for cr in all_concept_rows:
        dom = cr["domain_id"] or "general_pharmacology"
        if dom not in domain_map:
            display_name = dom.replace("_", " ").title()
            domain_map[dom] = {
                "domain_id": dom,
                "display_name": display_name,
                "total_questions": 0,
                "concepts": []
            }
        domain_map[dom]["total_questions"] += cr["question_count"]
        domain_map[dom]["concepts"].append({
            "concept_id": cr["concept_id"],
            "name": cr["concept_name"],
            "question_count": cr["question_count"]
        })

    total_eligible = len(rows)
    per_concept: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        cid = r["concept_id"]
        if cid not in per_concept:
            per_concept[cid] = {
                "concept_id": cid,
                "concept_name": r["concept_name"],
                "domain_id": r["domain_id"],
                "eligible_count": 0
            }
        per_concept[cid]["eligible_count"] += 1

    capped_count = min(req.requested_count, total_eligible)
    coverage_gaps = []
    if req.requested_count > total_eligible:
        shortfall = req.requested_count - total_eligible
        coverage_gaps.append(
            f"Requested {req.requested_count} questions, but only {total_eligible} eligible verified questions exist for the selected scope ({shortfall} question shortfall)."
        )

    return {
        "requested_count": req.requested_count,
        "eligible_count": total_eligible,
        "achievable_count": capped_count,
        "is_achievable": req.requested_count <= total_eligible and total_eligible > 0,
        "coverage_gaps": coverage_gaps,
        "concepts_breakdown": list(per_concept.values()),
        "available_domains": list(domain_map.values()),
        "estimated_duration_minutes": round(max(1, capped_count) * 1.8),
        "marking_scheme": {
            "correct_marks": 4.0,
            "negative_marks": 1.0,
            "unattempted_marks": 0.0,
            "rule": "Authoritative GPAT NBEMS Marking Scheme (+4 / -1)"
        }
    }

@app.post("/api/mock/{exam_id}/start")
def start_mock(
    exam_id: str,
    user_id: str = Query("student_01"),
    engine: MockExamEngine = Depends(get_mock_engine)
):
    """Starts server timer and sets status to IN_PROGRESS."""
    return engine.start_mock_exam(exam_id=exam_id, user_id=user_id)

@app.get("/api/mock/{exam_id}")
def get_mock(
    exam_id: str,
    user_id: str = Query("student_01"),
    engine: MockExamEngine = Depends(get_mock_engine)
):
    """Retrieves full mock session with question sequence, recorded answers, and server-remaining seconds."""
    return engine.get_mock_exam(exam_id=exam_id, user_id=user_id)

@app.post("/api/mock/{exam_id}/answer")
def record_mock_answer(
    exam_id: str,
    req: MockAnswerRequest,
    engine: MockExamEngine = Depends(get_mock_engine)
):
    """Saves answer option, confidence, and millisecond timing for question."""
    return engine.record_mock_answer(
        exam_id=exam_id,
        user_id=req.user_id,
        question_id=req.question_id,
        selected_option=req.selected_option,
        time_spent_ms=req.time_spent_ms,
        confidence=req.confidence
    )

@app.post("/api/mock/{exam_id}/pause")
def pause_mock(
    exam_id: str,
    user_id: str = Query("student_01"),
    engine: MockExamEngine = Depends(get_mock_engine)
):
    """Pauses exam and freezes timer."""
    return engine.pause_mock_exam(exam_id=exam_id, user_id=user_id)

@app.post("/api/mock/{exam_id}/submit")
def submit_mock(
    exam_id: str,
    user_id: str = Query("student_01"),
    engine: MockExamEngine = Depends(get_mock_engine)
):
    """Submits exam, runs MockScorer, performs 4-quadrant diagnostic analysis, and records feedback."""
    return engine.submit_mock_exam(exam_id=exam_id, user_id=user_id)

@app.get("/api/mock/history")
def mock_history(
    user_id: str = Query("student_01"),
    engine: MockExamEngine = Depends(get_mock_engine)
):
    """Returns list of past completed or in-progress mock exams."""
    return {"history": engine.list_mock_history(user_id=user_id)}

# --- System Self-Evaluation & Regression Endpoints ---

@app.post("/api/evaluation/run")
def run_evaluation(
    req: EvaluationRunRequest,
    runner: EvaluationRunner = Depends(get_eval_runner)
):
    """Executes the full evaluation test suite (100 retrieval, 100 answers, 50 citations, 50 traps)."""
    return runner.run_full_evaluation(version=req.version)

@app.get("/api/evaluation/latest")
def latest_evaluation(
    runner: EvaluationRunner = Depends(get_eval_runner)
):
    """Returns latest evaluation report."""
    latest = runner.get_latest_evaluation()
    if not latest:
        raise HTTPException(status_code=404, detail="No evaluation run found. Trigger POST /api/evaluation/run first.")
    return latest

@app.get("/api/evaluation/history")
def evaluation_history(
    runner: EvaluationRunner = Depends(get_eval_runner)
):
    """Returns chronological list of evaluation runs and regression states."""
    return {"history": runner.list_evaluation_history()}

# --- Admin & Observability Endpoints (Protected) ---

@app.get("/api/admin/metrics")
def get_admin_dashboard(
    _auth: bool = Depends(verify_admin_access),
    admin: AdminObservabilityService = Depends(get_admin_service)
):
    """Returns comprehensive production metrics for system, knowledge, questions, and learner telemetry."""
    return admin.get_full_dashboard()

@app.post("/api/admin/backup/create")
def trigger_backup(
    _auth: bool = Depends(verify_admin_access)
):
    """Triggers an online non-blocking SQLite database snapshot with checksum and gzip compression."""
    manifest = create_backup(db_path=Path(DB_PATH))
    return {"status": "SUCCESS", "manifest": manifest}

@app.get("/api/admin/backups")
def get_backup_list(
    _auth: bool = Depends(verify_admin_access)
):
    """Lists existing local compressed database backups."""
    return {"backups": list_backups()}

# --- Pilot Control & Real-Learner Telemetry Endpoints ---

class PilotToggleRequest(BaseModel):
    enabled: bool

class PilotRegisterRequest(BaseModel):
    is_synthetic: bool = False
    consent_given: bool = True

class PilotFeedbackRequest(BaseModel):
    student_id: str
    feedback_type: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    question_id: Optional[str] = None
    comment: Optional[str] = None

@app.get("/api/pilot/status")
def get_pilot_status(
    pilot: PilotService = Depends(get_pilot_service)
):
    """Returns current pilot operational status and capacity."""
    return pilot.get_pilot_status()

@app.post("/api/admin/pilot/toggle")
def toggle_pilot_status(
    req: PilotToggleRequest,
    _auth: bool = Depends(verify_admin_access),
    pilot: PilotService = Depends(get_pilot_service)
):
    """Enables or disables controlled pilot access. (Protected)"""
    new_status = pilot.set_pilot_enabled(req.enabled)
    return {"pilot_enabled": new_status, "status": "SUCCESS"}

@app.post("/api/pilot/register")
def register_pilot_learner(
    req: PilotRegisterRequest,
    pilot: PilotService = Depends(get_pilot_service)
):
    """Enrolls a pseudonymous pilot learner or synthetic test account."""
    return pilot.register_pilot_learner(
        is_synthetic=req.is_synthetic,
        consent_given=req.consent_given
    )

@app.post("/api/pilot/feedback")
def submit_pilot_feedback(
    fb: PilotFeedbackRequest,
    pilot: PilotService = Depends(get_pilot_service)
):
    """Collects real learner feedback on questions, explanations, distractors, or bugs."""
    pilot.authenticate_learner(fb.student_id)
    return pilot.record_feedback(
        student_id=fb.student_id,
        feedback_type=fb.feedback_type,
        rating=fb.rating,
        question_id=fb.question_id,
        comment=fb.comment
    )

@app.get("/api/admin/pilot/metrics")
def get_pilot_aggregated_metrics(
    _auth: bool = Depends(verify_admin_access),
    pilot: PilotService = Depends(get_pilot_service)
):
    """Returns privacy-safe aggregated pilot performance metrics. (Protected)"""
    return pilot.get_aggregated_metrics()

# Serve PWA Frontend Static Files, Admin Portal, and Manifest
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "public"

@app.get("/admin")
@app.get("/admin/")
def serve_admin(
    _auth: bool = Depends(verify_admin_access)
):
    return FileResponse(FRONTEND_DIR / "admin.html")

@app.get("/")
@app.get("/index.html")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/manifest.json")
def serve_manifest():
    return FileResponse(FRONTEND_DIR / "manifest.json", media_type="application/manifest+json")

@app.get("/sw.js")
def serve_sw():
    return FileResponse(FRONTEND_DIR / "sw.js", media_type="application/javascript")

if MEDIA_DIR.exists():
    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
