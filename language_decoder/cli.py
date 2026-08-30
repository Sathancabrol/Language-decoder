"""
Language-decoder — Command line interface
=========================================

    python -m language_decoder.cli decode --input PATH [--title TITLE]
    python -m language_decoder.cli decode --text "…" [--json]
    python -m language_decoder.cli serve [--port 9000]

`decode` runs the full human-decoding pipeline and writes
`ui/data/profile.json` (the file the interface reads).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .profile import decode_human
from . import VERSION

REPO_DATA = Path(__file__).resolve().parent.parent / "ui" / "data" / "profile.json"


def _read_input(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    suffix = path.suffix.lower()
    if suffix in (".json", ".jsonl"):
        # structured items / ai proposal
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw
    return path.read_text(encoding="utf-8")


def find_output(no_write: bool) -> Path:
    return REPO_DATA


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="language-decoder", description=VERSION_DESC)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_decode = sub.add_parser("decode", help="Decode a human from text / items / AI JSON.")
    p_decode.add_argument("--input", help="Path to input file (.txt/.md/.json).")
    p_decode.add_argument("--text", help="Inline text to decode.")
    p_decode.add_argument("--items", help="Path to structured items JSON.")
    p_decode.add_argument("--ai", help="Path to LLM proposal JSON (guarded).")
    p_decode.add_argument("--title", default="Décodage humain")
    p_decode.add_argument("--person", default="h-001")
    p_decode.add_argument("--year", type=int, default=2026)
    p_decode.add_argument("--no-write", action="store_true",
                          help="Print to stdout instead of writing ui/data/profile.json.")
    p_decode.add_argument("--word", action="store_true", help="Word-wrap the text output.")

    p_serve = sub.add_parser("serve", help="Serve the UI + engine output.")
    p_serve.add_argument("--port", type=int, default=9000)

    args = parser.parse_args(argv)

    if args.cmd == "decode":
        return _cmd_decode(args)
    if args.cmd == "serve":
        from .serve import serve
        serve(args.port)
        return 0
    return 1


def _cmd_decode(args) -> int:
    text: str = ""
    items: list[dict] | None = None
    ai_json: str = ""

    if args.input:
        raw = _read_input(Path(args.input))
        if isinstance(raw, list):
            items = raw
        else:
            text = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
    elif args.text:
        text = args.text
    elif args.items:
        items = json.loads(Path(args.items).read_text(encoding="utf-8"))
        if not isinstance(items, list):
            items = [items]
    elif args.ai:
        ai_json = Path(args.ai).read_text(encoding="utf-8")
    else:
        print("Error: provide --input, --text, --items or --ai.", file=sys.stderr)
        return 2

    profile = decode_human(
        text=text, items=items, ai_json=ai_json,
        source_title=args.title, person_id=args.person, current_year=args.year,
    )
    out = profile.to_json(indent=2)

    if args.no_write:
        print(out)
        return 0

    REPO_DATA.parent.mkdir(parents=True, exist_ok=True)
    REPO_DATA.write_text(out, encoding="utf-8")

    # Human readable summary
    print(json.dumps({
        "wrote": str(REPO_DATA),
        "id": profile.id,
        "source_title": profile.source_title,
        "estimates": sum(len(d.estimates) for d in profile.domains.values()),
        "refusals": len(profile.refusals),
        "functioning": len(profile.functioning),
        "dynamics_retentions": len(profile.dynamics.get("retentions", [])),
    }, ensure_ascii=False, indent=2))
    print("\nRécapitulatif par domaine :")
    for domain, block in profile.domains.items():
        print(f"  {block.title:<18} {len(block.estimates):>2} estimations, "
              f"{len(block.refusals):>2} refus, "
              f"{len(block.observations):>3} observations")
    return 0


VERSION_DESC = ("Décodeur humain — caractéristiques physiques, mentales, capacité "
                "d'action et fonctionnement (modèle épistémique, voir docs/).")

if __name__ == "__main__":
    raise SystemExit(main())
