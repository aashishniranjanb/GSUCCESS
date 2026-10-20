import pytest
import sqlite3
import json
import hashlib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BASELINE_DB = ROOT_DIR / "data" / "gpat_baseline.db"
SOURCE_MANIFEST = ROOT_DIR / "baseline" / "source_manifest.json"

@pytest.fixture
def baseline_conn():
    conn = sqlite3.connect(str(BASELINE_DB))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

def test_source_manifest_files_exist_and_hash():
    """Verify that all source PDFs in the manifest exist on disk and match their SHA-256 fingerprints."""
    with open(SOURCE_MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert len(manifest) >= 6

    for item in manifest:
        pdf_path = Path(item["original_path"])
        assert pdf_path.exists(), f"Source file does not exist: {pdf_path}"

        # Verify SHA-256
        hasher = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        calculated_hash = hasher.hexdigest()
        assert calculated_hash == item["sha256"], f"Hash mismatch for {item['filename']}"

def test_chunk_provenance_and_dimensions(baseline_conn):
    """Verify that all baseline_chunks reference valid registered sources and 384-dim embeddings."""
    cur = baseline_conn.cursor()
    cur.execute("SELECT count(*) FROM baseline_chunks")
    total_chunks = cur.fetchone()[0]
    assert total_chunks == 505

    # Check that every chunk references an authentic source_id
    cur.execute("SELECT DISTINCT source_id FROM baseline_chunks")
    chunk_sources = set(r[0] for r in cur.fetchall())

    cur.execute("SELECT source_id FROM baseline_sources")
    registered_sources = set(r[0] for r in cur.fetchall())

    assert chunk_sources.issubset(registered_sources), "Unregistered sources found in baseline_chunks"

    # Check embedding dimensions
    cur.execute("SELECT count(*) FROM baseline_chunks WHERE dimensions != 384")
    assert cur.fetchone()[0] == 0, "Non-384 dimensional embedding detected"

def test_quarantined_questions_exclusion(baseline_conn):
    """Verify that the 89 quarantined items in pyq_review_queue are tracked with non-published status."""
    cur = baseline_conn.cursor()
    cur.execute("SELECT count(*) FROM pyq_review_queue")
    quarantined_count = cur.fetchone()[0]
    assert quarantined_count == 89

    # Verify that pyq_review_queue correctly flags items as PENDING_REVIEW
    cur.execute("SELECT DISTINCT status FROM pyq_review_queue")
    statuses = set(r[0] for r in cur.fetchall())
    assert "PENDING_REVIEW" in statuses
