import sqlite3
import json

def run_eval():
    conn = sqlite3.connect('gpat_knowledge.db')
    cur = conn.cursor()

    eval_cases = []
    with open('knowledge_base/evaluations/ans_baseline_eval.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                eval_cases.append(json.loads(line))

    results = []
    top_1_hits = 0
    top_3_hits = 0

    for case in eval_cases:
        cid = case['concept_id']
        cur.execute('''
            SELECT b.id, b.page_number, b.content, b.document_id
            FROM content_blocks b
            JOIN block_concept_mappings m ON m.block_id = b.id
            WHERE m.concept_id = ?
            ORDER BY b.page_number
        ''', (cid,))
        mapped_blocks = cur.fetchall()
        
        expected_page = case['expected_source_page']
        retrieved_pages = [b[1] for b in mapped_blocks]
        
        is_top1 = len(retrieved_pages) > 0 and retrieved_pages[0] == expected_page
        is_top3 = expected_page in retrieved_pages[:3]
        
        if is_top1:
            top_1_hits += 1
        if is_top3:
            top_3_hits += 1
        
        results.append({
            'query_id': case['query_id'],
            'concept_id': cid,
            'expected_page': expected_page,
            'retrieved_pages': retrieved_pages[:5],
            'top_1_match': is_top1,
            'top_3_match': is_top3
        })

    metrics = {
        'total_cases': len(eval_cases),
        'top_1_accuracy': (top_1_hits / len(eval_cases)) * 100 if eval_cases else 0,
        'top_3_accuracy': (top_3_hits / len(eval_cases)) * 100 if eval_cases else 0,
        'details': results
    }

    with open('knowledge_base/evaluations/baseline_metrics.json', 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    print(f"Evaluated {len(eval_cases)} cases:")
    print(f"  Top-1 Citation Match: {metrics['top_1_accuracy']:.1f}%")
    print(f"  Top-3 Citation Match: {metrics['top_3_accuracy']:.1f}%")

    conn.close()

if __name__ == '__main__':
    run_eval()
