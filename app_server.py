import os
import sys
import io
import json
import sqlite3
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

from learner_engine import LearnerEngine
from retrieval_and_eval import search_knowledge_base
from vector_index import VectorIndexEngine
from knowledge_graph import KnowledgeGraphEngine

DB_PATH = "gpat_knowledge.db"
PORT = 8080
vector_engine = VectorIndexEngine()
kg_engine = KnowledgeGraphEngine()


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GPAT 2027 — AI Learning Operating System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --bg: #f8fafc;
      --surface: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --muted: #64748b;
      --success: #16a34a;
      --danger: #dc2626;
      --warning: #d97706;
      --radius: 10px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
    header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
    .brand { display: flex; align-items: center; gap: 0.75rem; }
    .brand-title { font-size: 1.25rem; font-weight: 700; color: #1e293b; letter-spacing: -0.02em; }
    .brand-badge { background: #dbeafe; color: #1e40af; font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.5rem; border-radius: 9999px; }
    nav { display: flex; gap: 0.5rem; }
    .nav-btn { background: transparent; border: none; padding: 0.5rem 1rem; border-radius: var(--radius); font-weight: 500; color: var(--muted); cursor: pointer; transition: all 0.15s; }
    .nav-btn:hover { color: var(--text); background: #f1f5f9; }
    .nav-btn.active { color: var(--primary); background: #eff6ff; font-weight: 600; }
    
    main { max-width: 1050px; margin: 2rem auto; padding: 0 1.5rem; }
    .tab-content { display: none; }
    .tab-content.active { display: block; animation: fadeIn 0.2s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .card-title { font-size: 1.15rem; font-weight: 600; color: #1e293b; }
    
    /* Buttons & Controls */
    .btn { background: var(--primary); color: white; border: none; padding: 0.55rem 1.1rem; border-radius: 6px; font-weight: 500; cursor: pointer; transition: all 0.15s; display: inline-flex; align-items: center; gap: 0.5rem; }
    .btn:hover { background: var(--primary-hover); }
    .btn-secondary { background: #f1f5f9; color: #334155; }
    .btn-secondary:hover { background: #e2e8f0; }

    /* Session Area */
    .session-config { display: flex; gap: 1rem; align-items: center; margin-bottom: 1.5rem; }
    .q-box { border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1.25rem; background: #fff; }
    .q-meta { display: flex; justify-content: space-between; font-size: 0.825rem; color: var(--muted); margin-bottom: 0.5rem; font-weight: 500; }
    .q-text { font-size: 1.05rem; font-weight: 600; margin-bottom: 1rem; color: #0f172a; }
    .options-grid { display: flex; flex-direction: column; gap: 0.6rem; }
    .option-item { display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.8rem 1rem; border: 1px solid var(--border); border-radius: 8px; cursor: pointer; transition: all 0.15s; background: #fff; }
    .option-item:hover { border-color: #cbd5e1; background: #f8fafc; }
    .option-item.selected { border-color: var(--primary); background: #eff6ff; }
    .option-item.correct { border-color: var(--success); background: #f0fdf4; color: #14532d; font-weight: 500; }
    .option-item.incorrect { border-color: var(--danger); background: #fef2f2; color: #7f1d1d; }
    .feedback-box { margin-top: 1rem; padding: 1rem; border-radius: 8px; font-size: 0.925rem; }
    .feedback-box.correct { background: #dcfce7; border: 1px solid #bbf7d0; color: #166534; }
    .feedback-box.incorrect { background: #fee2e2; border: 1px solid #fecaca; color: #991b1b; }
    .cue-badge { background: #fef3c7; color: #92400e; padding: 0.35rem 0.65rem; border-radius: 6px; font-size: 0.825rem; font-weight: 600; display: inline-block; margin-top: 0.5rem; }

    /* Tables */
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th { text-align: left; padding: 0.75rem 1rem; background: #f8fafc; color: var(--muted); font-weight: 600; border-bottom: 1px solid var(--border); }
    td { padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); }
    tr:hover td { background: #f8fafc; }

    /* Badges & Search */
    .search-bar { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; }
    .search-input { flex: 1; padding: 0.65rem 1rem; border: 1px solid var(--border); border-radius: var(--radius); font-size: 0.95rem; outline: none; }
    .search-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
    .citation-card { border-left: 3px solid var(--primary); padding: 0.75rem 1rem; background: #f8fafc; margin-bottom: 0.75rem; border-radius: 0 8px 8px 0; }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-title">GPAT 2027</div>
      <span class="brand-badge">Learning OS</span>
    </div>
    <nav>
      <button class="nav-btn active" onclick="showTab('session')">Today's Session</button>
      <button class="nav-btn" onclick="showTab('learn')">Learn</button>
      <button class="nav-btn" onclick="showTab('recall')">Recall (Q&A)</button>
      <button class="nav-btn" onclick="showTab('library')">Library</button>
      <button class="nav-btn" onclick="showTab('progress')">Progress</button>
    </nav>
  </header>

  <main>
    <!-- TAB 1: TODAY'S SESSION -->
    <section id="tab-session" class="tab-content active">
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Daily Adaptive Session</h2>
            <p style="font-size:0.875rem; color:var(--muted); margin-top:0.2rem;">
              Targeted active recall scheduled by FSRS memory models and misconception detection.
            </p>
          </div>
          <div class="session-config">
            <select id="session-duration" class="search-input" style="padding:0.45rem 0.8rem;">
              <option value="15">15 Min Session</option>
              <option value="30">30 Min Session</option>
              <option value="60">60 Min Session</option>
            </select>
            <button class="btn" onclick="startSession()">Start Session</button>
          </div>
        </div>

        <div id="session-container">
          <div style="text-align:center; padding:3rem; color:var(--muted);">
            Click <strong>Start Session</strong> to generate your personalized active recall deck.
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 2: LEARN -->
    <section id="tab-learn" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Pharmacology Concept Ontology</h2>
          <span style="font-size:0.85rem; color:var(--muted);">34 Canonical Concepts</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Concept</th>
              <th>Domain</th>
              <th>Objective</th>
              <th>Exam Priority</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="concepts-tbody">
            <tr><td colspan="5" style="text-align:center;">Loading concepts...</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- TAB 3: RECALL (Q&A) -->
    <section id="tab-recall" class="tab-content">
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Source-Grounded Recall Tutor</h2>
            <p style="font-size:0.875rem; color:var(--muted); margin-top:0.2rem;">
              Answers verified directly against KD Tripathi & Dr. Rajesh Choudhary review notes with page citations.
            </p>
          </div>
        </div>
        <div class="search-bar">
          <input type="text" id="tutor-query" class="search-input" placeholder="Ask a pharmacology question (e.g., Why is Atropine contraindicated in glaucoma?)...">
          <button class="btn" onclick="submitTutorQuery()">Ask Tutor</button>
        </div>
        <div id="tutor-results"></div>
      </div>

      <!-- Relational Knowledge Graph Reasoning Card -->
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Relational Knowledge Graph & Multi-Hop Pathway</h2>
            <p style="font-size:0.875rem; color:var(--muted); margin-top:0.2rem;">
              Explore explicit mechanism chains and Section 11 Evidence Contracts (e.g. Drug ➔ Target ➔ Secondary Messenger ➔ Physiological Effect).
            </p>
          </div>
          <span class="brand-badge" style="background:#fef3c7; color:#92400e;">42 Nodes • 33 Relational Edges</span>
        </div>
        <div class="search-bar">
          <input type="text" id="kg-start" class="search-input" style="flex: 1;" placeholder="Start Entity (e.g. Atropine, Captopril, Levodopa)...">
          <input type="text" id="kg-end" class="search-input" style="flex: 1;" placeholder="End Entity / Effect (e.g. Organophosphates, Persistent Dry Cough, Parkinson's Disease)...">
          <button class="btn" style="background:#059669;" onclick="submitGraphReason()">Traverse Pathway</button>
        </div>
        <div id="kg-results"></div>
      </div>
    </section>

    <!-- TAB 4: LIBRARY -->
    <section id="tab-library" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Ingested Source Documents</h2>
        </div>
        <table>
          <thead>
            <tr>
              <th>Document Title</th>
              <th>File Name</th>
              <th>Total Pages</th>
              <th>Authority</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Pharmacology Key Points for GPAT</strong></td>
              <td><code>Pharmacology-complete.pdf</code></td>
              <td>121</td>
              <td>Standard Textbook (Level 3)</td>
              <td><span style="color:var(--success); font-weight:600;">✓ Ingested</span></td>
            </tr>
            <tr>
              <td><strong>Essentials of Medical Pharmacology (KD Tripathi)</strong></td>
              <td><code>Essentials of Medical Pharmacology.pdf</code></td>
              <td>1,020</td>
              <td>Primary Authority (Level 4)</td>
              <td><span style="color:var(--muted);">Queued</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- TAB 5: PROGRESS -->
    <section id="tab-progress" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Student Memory Matrix & Mastery</h2>
          <span class="brand-badge">FSRS v6 Active</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Concept</th>
              <th>Mastery</th>
              <th>FSRS Stability</th>
              <th>Attempts</th>
              <th>Misconceptions</th>
            </tr>
          </thead>
          <tbody id="progress-tbody">
            <tr><td colspan="5" style="text-align:center;">Loading memory state...</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>

  <script>
    function showTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
      document.getElementById('tab-' + tabId).classList.add('active');
      event.target.classList.add('active');

      if (tabId === 'learn') loadConcepts();
      if (tabId === 'progress') loadProgress();
    }

    async function startSession() {
      const duration = document.getElementById('session-duration').value;
      const res = await fetch(`/api/session?minutes=${duration}`);
      const data = await res.json();
      
      const container = document.getElementById('session-container');
      if (!data.questions || data.questions.length === 0) {
        container.innerHTML = `<p style="text-align:center; padding:2rem;">No questions available.</p>`;
        return;
      }

      let html = `<div style="margin-bottom:1rem; font-size:0.9rem; color:var(--muted);">
        Generated <strong>${data.questions.length}</strong> active recall questions.
      </div>`;

      data.questions.forEach((q, qIndex) => {
        html += `
          <div class="q-box" id="qbox-${q.question_id}">
            <div class="q-meta">
              <span><strong>Concept:</strong> ${q.concept_name}</span>
              <span>Source: p. ${q.source_page}</span>
            </div>
            <div class="q-text">${qIndex + 1}. ${q.question_text}</div>
            <div class="options-grid" id="opts-${q.question_id}">
              ${q.options.map((opt, oIdx) => `
                <div class="option-item" onclick="submitAnswer('${q.question_id}', ${oIdx})">
                  <span style="font-weight:600; min-width:20px;">[${String.fromCharCode(65 + oIdx)}]</span>
                  <span>${opt}</span>
                </div>
              `).join('')}
            </div>
            <div id="feedback-${q.question_id}"></div>
          </div>
        `;
      });
      container.innerHTML = html;
    }

    async function submitAnswer(qId, selectedOption) {
      const qBox = document.getElementById('qbox-' + qId);
      const optsGrid = document.getElementById('opts-' + qId);
      const feedbackDiv = document.getElementById('feedback-' + qId);

      const res = await fetch('/api/attempt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: 'student_01',
          question_id: qId,
          selected_option: selectedOption,
          response_time_sec: 14.2,
          confidence: 4
        })
      });
      const data = await res.json();

      Array.from(optsGrid.children).forEach((el, idx) => {
        el.style.pointerEvents = 'none';
        if (idx === data.correct_option) el.classList.add('correct');
        if (idx === selectedOption && !data.is_correct) el.classList.add('incorrect');
      });

      if (data.is_correct) {
        feedbackDiv.innerHTML = `
          <div class="feedback-box correct">
            <strong>✓ Correct!</strong><br>
            ${data.explanation}
            <div style="margin-top:0.4rem; font-size:0.8rem; color:#15803d;">
              FSRS Rating: <strong>${data.fsrs_rating}</strong> • Memory Stability: <strong>${data.stability_days} days</strong>
            </div>
          </div>
        `;
      } else {
        feedbackDiv.innerHTML = `
          <div class="feedback-box incorrect">
            <strong>✗ Incorrect</strong><br>
            ${data.distractor_reason ? `<em>Misconception:</em> ${data.distractor_reason}<br>` : ''}
            <div style="margin-top:0.4rem;">${data.explanation}</div>
            <div style="margin-top:0.4rem; font-size:0.8rem; color:#b91c1c;">
              FSRS Rating: <strong>${data.fsrs_rating}</strong> • Scheduled for Immediate Due Review
            </div>
          </div>
        `;
      }
    }

    async function loadConcepts() {
      const res = await fetch('/api/concepts');
      const concepts = await res.json();
      const tbody = document.getElementById('concepts-tbody');
      tbody.innerHTML = concepts.map(c => `
        <tr>
          <td><strong>${c.name}</strong></td>
          <td><code>${c.domain_id.replace('_pharmacology','')}</code></td>
          <td>${c.learning_objective}</td>
          <td><span style="font-weight:600; color:var(--primary);">${c.importance_score}/10</span></td>
          <td><span style="color:var(--success);">Active</span></td>
        </tr>
      `).join('');
    }

    async function loadProgress() {
      const res = await fetch('/api/progress?student_id=student_01');
      const progress = await res.json();
      const tbody = document.getElementById('progress-tbody');
      tbody.innerHTML = progress.map(p => `
        <tr>
          <td><strong>${p.name}</strong></td>
          <td>${Math.round(p.mastery * 100)}%</td>
          <td>${p.stability > 0 ? p.stability.toFixed(1) + ' days' : '-'}</td>
          <td>${p.attempts}</td>
          <td><span style="${p.misconception_count > 0 ? 'color:var(--danger); font-weight:600;' : ''}">${p.misconception_count}</span></td>
        </tr>
      `).join('');
    }

    async function submitTutorQuery() {
      const q = document.getElementById('tutor-query').value.trim();
      if (!q) return;
      const resDiv = document.getElementById('tutor-results');
      resDiv.innerHTML = `<p style="padding:1rem; color:var(--muted);">Searching verified textbook chunks...</p>`;
      
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      
      if (!data.blocks || data.blocks.length === 0) {
        resDiv.innerHTML = `<p style="padding:1rem; color:var(--muted);">No matching textbook evidence found.</p>`;
        return;
      }

      let html = `<div style="margin-top:1.5rem;"><h3 style="font-size:1rem; margin-bottom:0.75rem;">Verified Evidence from Pharmacology-complete.pdf:</h3>`;
      data.blocks.forEach(b => {
        html += `
          <div class="citation-card">
            <div style="font-size:0.8rem; font-weight:600; color:var(--muted); margin-bottom:0.25rem;">
              PAGE ${b.page_number} • ${b.heading_path.join(' > ') || 'General Pharmacology'}
            </div>
            <div style="font-size:0.925rem; color:#1e293b;">
              "${b.content}"
            </div>
          </div>
        `;
      });
      html += `</div>`;
      resDiv.innerHTML = html;
    }

    async function submitGraphReason() {
      const start = document.getElementById('kg-start').value.trim();
      const end = document.getElementById('kg-end').value.trim();
      if (!start || !end) return;
      
      const resDiv = document.getElementById('kg-results');
      resDiv.innerHTML = `<p style="padding:1rem; color:var(--muted);">Traversing relational knowledge graph and building Evidence Contract...</p>`;
      
      const res = await fetch(`/api/graph_reason?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
      const contract = await res.json();
      
      if (!contract.traversal_path || contract.traversal_path.length === 0) {
        resDiv.innerHTML = `<div class="feedback-box incorrect" style="margin-top:1rem;"><strong>No path found:</strong> ${contract.answer}</div>`;
        return;
      }
      
      let html = `
        <div style="margin-top:1.25rem; border:1px solid #a7f3d0; background:#f0fdf4; border-radius:8px; padding:1.25rem;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <strong style="color:#065f46; font-size:1.05rem;">Relational Pathway Traversal</strong>
            <span style="background:#10b981; color:white; font-size:0.75rem; font-weight:600; padding:0.2rem 0.6rem; border-radius:9999px;">Confidence ${(contract.confidence * 100).toFixed(0)}%</span>
          </div>
          <div style="margin-bottom:1rem; padding:0.75rem; background:white; border:1px solid #d1fae5; border-radius:6px; font-family:monospace; font-size:0.9rem; color:#047857;">
            ${contract.traversal_path.map(s => `<div>➔ ${s}</div>`).join('')}
          </div>
          <p style="font-size:0.95rem; color:#1e293b; line-height:1.6; margin-bottom:1rem;">
            ${contract.answer}
          </p>
          <div style="font-size:0.85rem; font-weight:600; color:#065f46; margin-bottom:0.5rem;">Section 11 Evidence Claims:</div>
          <div style="display:flex; flex-direction:column; gap:0.5rem;">
            ${contract.claims.map(c => `
              <div style="background:white; border-left:3px solid #10b981; padding:0.5rem 0.75rem; border-radius:0 6px 6px 0; font-size:0.875rem;">
                <strong>Claim:</strong> ${c.claim}<br>
                <span style="color:var(--muted); font-size:0.8rem;">Page ${c.evidence[0].page} • ${c.evidence[0].excerpt}</span>
              </div>
            `).join('')}
          </div>
        </div>
      `;
      resDiv.innerHTML = html;
    }
  </script>
</body>
</html>
"""

class GPATHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return
            
        elif path == "/api/session":
            minutes = int(query.get("minutes", [15])[0])
            engine = LearnerEngine()
            session = engine.generate_daily_session("student_01", session_minutes=minutes)
            self.send_json(session)
            return
            
        elif path == "/api/concepts":
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id, name, domain_id, learning_objective, importance_score, difficulty FROM concepts ORDER BY importance_score DESC")
            rows = [
                {"id": r[0], "name": r[1], "domain_id": r[2], "learning_objective": r[3], "importance_score": r[4], "difficulty": r[5]}
                for r in cur.fetchall()
            ]
            conn.close()
            self.send_json(rows)
            return
            
        elif path == "/api/progress":
            student_id = query.get("student_id", ["student_01"])[0]
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
            SELECT c.name, COALESCE(m.mastery, 0.0), COALESCE(m.stability, 0.0), 
                   COALESCE(m.attempts, 0), COALESCE(m.misconception_count, 0)
            FROM concepts c
            LEFT JOIN concept_memory_state m ON c.id = m.concept_id AND m.student_id = ?
            ORDER BY c.importance_score DESC
            """, (student_id,))
            rows = [
                {"name": r[0], "mastery": r[1], "stability": r[2], "attempts": r[3], "misconception_count": r[4]}
                for r in cur.fetchall()
            ]
            conn.close()
            self.send_json(rows)
            return
            
        elif path == "/api/search":
            q = query.get("q", [""])[0]
            blocks = vector_engine.hybrid_search(q, top_k=4)
            self.send_json({"blocks": blocks})
            return
            
        elif path == "/api/graph_reason":
            start = query.get("start", [""])[0]
            end = query.get("end", [""])[0]
            contract = kg_engine.generate_evidence_contract(f"Mechanism connecting {start} and {end}", start, end)
            self.send_json(contract)
            return
            
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/attempt":
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body.decode('utf-8'))
            
            engine = LearnerEngine()
            feedback = engine.record_attempt(
                student_id=data.get("student_id", "student_01"),
                question_id=data["question_id"],
                selected_option=int(data["selected_option"]),
                response_time_sec=float(data.get("response_time_sec", 15.0)),
                confidence=int(data.get("confidence", 3))
            )
            self.send_json(feedback)
            return
            
        self.send_response(404)
        self.end_headers()

    def send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run_server():
    server = HTTPServer(("127.0.0.1", PORT), GPATHandler)
    print(f"\n==========================================")
    print(f"GPAT AI LEARNING OPERATING SYSTEM RUNNING")
    print(f"Local URL: http://127.0.0.1:{PORT}")
    print(f"==========================================\n")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
