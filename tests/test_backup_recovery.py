import unittest
import shutil
import sqlite3
import tempfile
from pathlib import Path
from scripts.backup_db import create_backup, rotate_backups, list_backups
from scripts.restore_db import verify_and_restore

class TestBackupRecovery(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / "test_gpat.db"
        self.backup_dir = self.test_dir / "backups"
        
        # Create dummy database
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("CREATE TABLE questions (id TEXT PRIMARY KEY, text TEXT)")
        cur.execute("CREATE TABLE candidate_claims (id TEXT PRIMARY KEY, claim TEXT)")
        cur.execute("INSERT INTO questions VALUES ('q1', 'Atropine mechanism?')")
        cur.execute("INSERT INTO candidate_claims VALUES ('c1', 'Atropine is muscarinic antagonist')")
        conn.commit()
        conn.close()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_backup_and_restore(self):
        # 1. Create backup
        manifest = create_backup(db_path=self.db_path, backup_dir=self.backup_dir, retention_count=3)
        self.assertTrue(Path(manifest["backup_path"]).exists())
        self.assertEqual(manifest["table_counts"]["questions"], 1)
        self.assertEqual(manifest["table_counts"]["candidate_claims"], 1)

        # 2. Modify database
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("DELETE FROM questions")
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM questions")
        self.assertEqual(cur.fetchone()[0], 0)
        conn.close()

        # 3. Restore database from backup
        restore_result = verify_and_restore(
            backup_file=Path(manifest["backup_path"]),
            target_db=self.db_path
        )
        self.assertEqual(restore_result["status"], "RESTORED_SUCCESSFULLY")
        self.assertEqual(restore_result["questions_restored"], 1)

        # 4. Verify contents restored
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM questions")
        self.assertEqual(cur.fetchone()[0], 1)
        conn.close()

    def test_rotation(self):
        # Create multiple backups
        for _ in range(5):
            create_backup(db_path=self.db_path, backup_dir=self.backup_dir, retention_count=3)
        
        backups = list_backups(backup_dir=self.backup_dir)
        self.assertLessEqual(len(backups), 3)

if __name__ == "__main__":
    unittest.main()
