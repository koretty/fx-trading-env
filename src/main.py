import sys
from pathlib import Path


def _bootstrap_src_path() -> None:
    src = Path(__file__).resolve().parent
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


_bootstrap_src_path()

from fx_trading_env.cli import main


if __name__ == "__main__":
    main()
