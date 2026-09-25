import os
import tempfile

# 必须在 import app.* 之前：让 config 指向临时数据库
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="floortile-test-")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
