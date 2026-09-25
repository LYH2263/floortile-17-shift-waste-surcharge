import os
import tempfile

import pytest

# Point the app at an isolated DB before any app.config import happens.
_TMP = tempfile.mkdtemp(prefix="floortile-test-")
os.environ["DATA_DIR"] = _TMP

from app import seed  # noqa: E402
from app.db import connect  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    """Recreate an empty, seeded database for every test."""
    db_path = os.path.join(_TMP, "app.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    seed.init_db()
    yield
    conn = connect()
    conn.close()
