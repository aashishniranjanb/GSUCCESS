import io
import sys
from learner_engine import LearnerEngine

def run_simulation():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    engine = LearnerEngine()
    student_id = "student_aspirant_2027"
    
    print("\n" + "=" * 65)
    print("SIMULATING ACTIVE RECALL LEARNER SESSION")
    print("Student: " + student_id)
    print("=" * 65 + "\n")
    
    # 1. Initial Session Generation
    session = engine.generate_daily_session(student_id, session_minutes=15)
    print(f"[STAGE 1]: Generated initial 15-minute adaptive session ({len(session['questions'])} questions)\n")
    
    # Question 1: Digoxin mechanism
    q1 = session["questions"][0]
    print(f"--- Question 1: {q1['concept_name']} ---")
    print(f"Text: {q1['question_text']}")
    print(f"Student selects Option 0 (Correct) in 12.4s with high confidence (5/5)...")
    res1 = engine.record_attempt(
        student_id=student_id,
        question_id=q1["question_id"],
        selected_option=0,
        response_time_sec=12.4,
        confidence=5
    )
    print(f"--> Result: Correct? {res1['is_correct']} | FSRS Rating: {res1['fsrs_rating']} | Stability: {res1['stability_days']} days | Next Review: {res1['next_due_date'][:16]}")
    
    # Question 2: Atropine in glaucoma (Simulate student error selecting distractor 2)
    q2 = session["questions"][1]
    print(f"\n--- Question 2: {q2['concept_name']} ---")
    print(f"Text: {q2['question_text']}")
    print(f"Student selects Option 2 (Incorrect misconception) in 18.0s...")
    res2 = engine.record_attempt(
        student_id=student_id,
        question_id=q2["question_id"],
        selected_option=2,
        response_time_sec=18.0,
        confidence=3
    )
    print(f"--> Result: Correct? {res2['is_correct']} | FSRS Rating: {res2['fsrs_rating']}")
    print(f"--> Distractor Explanation: \"{res2['distractor_reason']}\"")
    print(f"--> High-Yield Concept Cue: {q2['cue']}")
    print(f"--> Next Review Scheduled Immediately: {res2['next_due_date'][:16]}")
    
    # 2. Dynamic Re-scheduling
    print(f"\n[STAGE 2]: Regenerating Adaptive Session after learner feedback...")
    new_session = engine.generate_daily_session(student_id, session_minutes=15)
    print("New Prioritized Session Order:")
    for idx, q in enumerate(new_session["questions"][:4], 1):
        print(f"  {idx}. [{q['concept_name']}] Priority Score: {q['priority_score']:.1f} (Source Page {q['source_page']})")
        
    print("\n" + "=" * 65)
    print("SIMULATION COMPLETE: Adaptive Memory Loop Confirmed Active")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_simulation()
