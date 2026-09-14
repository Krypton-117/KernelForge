"""Run upstream PaperPipe with this repository's library and UTF-8."""
import os
from pathlib import Path
import site
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
env = dict(os.environ)
env["PAPER_DB_PATH"] = str(root / "data" / "papers")
env["PYTHONUTF8"] = "1"
env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
# pip's user scripts are not necessarily on Windows PATH.
user_scripts = Path(site.getuserbase()) / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts"
env["PATH"] = str(user_scripts) + os.pathsep + str(Path(sys.executable).parent/"Scripts") + os.pathsep + env.get("PATH", "")
raise SystemExit(subprocess.call([sys.executable, "-X", "utf8", "-m", "paperpipe", *sys.argv[1:]], env=env, cwd=root))
