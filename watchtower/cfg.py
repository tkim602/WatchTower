from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

OUT_DIR = Path(os.getenv("WATCHTOWER_OUTPUT_DIR", PROJECT_ROOT / "out"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

KO_JSON = Path(os.getenv("WATCHTOWER_SOURCE_JSON", PROJECT_ROOT / "examples" / "source_ko.json"))
EN_JSON = Path(os.getenv("WATCHTOWER_MT_JSON", PROJECT_ROOT / "examples" / "translation_en.json"))
TERMBASE_PATH = Path(os.getenv("WATCHTOWER_TERMBASE_JSON", PROJECT_ROOT / "examples" / "termbase.json"))

LIMIT = int(os.getenv("WATCHTOWER_LIMIT", "5"))
SEED = int(os.getenv("WATCHTOWER_SEED", "8084"))

COS_MODEL = os.getenv("WATCHTOWER_COS_MODEL", "sentence-transformers/LaBSE")
COMET_MODEL = os.getenv("WATCHTOWER_COMET_MODEL", "Unbabel/wmt22-cometkiwi-da")
GEMBA_MODEL = os.getenv("WATCHTOWER_GEMBA_MODEL", "gpt-4o-mini")
APE_MODEL = os.getenv("WATCHTOWER_APE_MODEL", "gpt-4o-mini")

# Public-demo defaults. These are included only to make the demo runnable and
# should not be interpreted as proprietary production tuning.
Q_SCORE_WEIGHTS = {"cos": 0.20, "comet": 0.30, "gemba": 0.50}
Q_SCORE_THRESHOLDS = {"fail": -0.6, "soft_pass": 0.25}

GEMBA_BATCH = int(os.getenv("WATCHTOWER_GEMBA_BATCH", "4"))
APE_CONCURRENCY = int(os.getenv("WATCHTOWER_APE_CONCURRENCY", "8"))
DEVICE = os.getenv("WATCHTOWER_DEVICE", "cpu")

FILTER_OUTPUT_FILENAME = "filtered.json"
GEMBA_OUTPUT_FILENAME = "gemba.json"
APE_OUTPUT_FILENAME = "ape.json"
