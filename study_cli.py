import sys
import io
import time
import sqlite3
from learner_engine import LearnerEngine
from grounded_tutor import ask_tutor

def print_banner():
    print("\n" + "=" * 65)
    print("        GPAT 2027 AI LEARNING OPERATING SYSTEM")
    print("  Active Recall • FSRS Spaced Repetition • Source-Grounded")
    print("=" * 65 + "\n")

def view_mastery_matrix(student_id: str = "student_01"):
    conn = sqlite3.connect("gpat_knowledge.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT c.name, c.domain_id, c.importance_score, 
           COALESCE(m.mastery, 0.0), COALESCE(m.stability, 0.0), 
           COALESCE(m.attempts, 0), COALESCE(m.misconception_count, 0)
    FROM concepts c
    LEFT JOIN concept_memory_state m ON c.id = m.concept_id AND m.student_id = ?
    ORDER BY c.importance_score DESC, c.domain_id ASC
    """, (student_id,))
    
    rows = cur.fetchall()
    print("\n" + "-" * 75)
    print(f"{'Concept Name':<35} | {'Domain':<15} | {'Mastery':<8} | {'Stability':<9} | {'Att.'}")
    print("-" * 75)
    for r in rows[:15]:
        name, domain, imp, mastery, stab, att, misc = r
        dom_short = domain.replace("_pharmacology", "")
        mastery_bar = f"{int(mastery * 100)}%"
        stab_str = f"{stab:.1f}d" if stab > 0 else "-"
        print(f"{name:<35} | {dom_short:<15} | {mastery_bar:<8} | {stab_str:<9} | {att}")
    print("-" * 75 + "\n")
    conn.close()

def run_session_interactive(student_id: str = "student_01", minutes: int = 15):
    engine = LearnerEngine()
    session = engine.generate_daily_session(student_id, session_minutes=minutes)
    
    print(f"\n[SESSION LAUNCHED]: {minutes}-minute Adaptive Study Session")
    print(f"Total Questions: {len(session['questions'])}\n")
    
    score = 0
    for idx, q in enumerate(session["questions"], 1):
        print(f"\n[{idx}/{len(session['questions'])}] Concept: {q['concept_name']} (Source: p. {q['source_page']})")
        print(f"Q: {q['question_text']}\n")
        
        for o_idx, opt in enumerate(q["options"]):
            print(f"  [{o_idx + 1}] {opt}")
            
        print("\nSelect Option (1-4) or 'q' to quit: ", end="", flush=True)
        user_in = input().strip()
        if user_in.lower() == 'q':
            break
            
        try:
            choice = int(user_in) - 1
        except ValueError:
            print("Invalid input, skipping...")
            continue
            
        t0 = time.time()
        # Record attempt
        feedback = engine.record_attempt(
            student_id=student_id,
            question_id=q["question_id"],
            selected_option=choice,
            response_time_sec=15.0,
            confidence=4
        )
        
        if feedback["is_correct"]:
            print("\n[CORRECT!]")
            score += 1
        else:
            print("\n[INCORRECT]")
            if feedback["distractor_reason"]:
                print(f"Why this option is a common trap: {feedback['distractor_reason']}")
                
        print(f"Explanation: {feedback['explanation']}")
        print(f"High-Yield Cue: {q['cue']}")
        print(f"FSRS Memory Rating: {feedback['fsrs_rating']} (Next Review: {feedback['next_due_date'][:10]})")
        print("-" * 50)
        
    print(f"\nSession Complete! Score: {score}/{len(session['questions'])}")

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print_banner()
    if len(sys.argv) > 1 and sys.argv[1] == "session":
        run_session_interactive()
    else:
        view_mastery_matrix()
