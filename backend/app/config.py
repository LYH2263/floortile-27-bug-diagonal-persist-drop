import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "app.db"

DEFAULT_WASTE_PCT = 8.0

# 斜铺（45° 对角铺贴）默认斜向折算系数与允许上限
DEFAULT_DIAG_FACTOR = 1.1
MAX_DIAG_FACTOR = 2.0
