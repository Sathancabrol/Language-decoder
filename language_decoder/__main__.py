"""Enable `python -m language_decoder …` (delegates to the CLI)."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
