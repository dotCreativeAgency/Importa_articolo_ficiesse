import subprocess
import tempfile
import os


def test_import_progress_dry_run(tmp_path):
    # prepare a small SQL file
    sql = "INSERT INTO `t_articoli` VALUES (1,'a',NULL,'t1','s1',NULL,'body',0,NULL,NULL,NULL,0,1,NULL,NULL,NULL);"
    file_path = tmp_path / "small.sql"
    file_path.write_text(sql, encoding='utf-8')

    db_path = tmp_path / "test.db"

    # Run import script in dry-run mode with progress (should exit 0)
    res = subprocess.run(["python3", "import_articoli_to_sqlite.py", str(file_path), "--db", str(db_path), "--dry-run", "--progress"], capture_output=True, text=True)
    print(res.stdout)
    assert res.returncode == 0
    # Check that dry-run line appears (DRY-RUN or similar)
    assert 'DRY-RUN' in res.stdout or 'Importazione' in res.stdout