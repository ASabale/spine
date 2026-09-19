from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from spine import __version__
from spine.artifacts import (
    board,
    claim,
    claimable_from_next,
    link,
    new_ticket,
    new_work_item,
    next_lines,
    release,
    read_meta,
    resolve_artifact,
    set_status,
    status_payload,
)
from spine.doctor import doctor, doctor_ok
from spine.errors import SpineError, exit_code_for
from spine.evolve import evolve, install_wires, set_pack
from spine.initcmd import init_target
from spine.model import SPEC_ROOT


def _root() -> Path:
    return Path.cwd()


def _print_next(root: Path) -> None:
    print("## Next")
    for line in next_lines(root):
        print(line if line.startswith("#") else f"- {line}")


def _emit_payload_or_next(root: Path, as_json: bool, *prose: str) -> None:
    if as_json:
        print(json.dumps(status_payload(root), indent=2))
        return
    for line in prose:
        print(line)
    if prose:
        print()
    _print_next(root)


def _add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="machine-readable output for agents",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="spine",
        description="Harness-agnostic process spine. CLI owns metadata; agents own content.",
        epilog="Sit-down: spine init → spine prime (or doctor then next). spine status is the board. The ## Next block (and `run` in --json) is the next command. cwd is always the process working directory (uv run --project, not --directory).",
    )
    parser.add_argument("--version", action="version", version=f"spine {__version__}")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json_root",
        help="machine-readable output for agents",
    )
    sub = parser.add_subparsers(dest="cmd", required=False)

    p_init = sub.add_parser("init", help="scaffold a target, then print Next")
    p_init.add_argument("--refresh", action="store_true")

    p_status = sub.add_parser("status", help="board plus the next command")
    _add_json_flag(p_status)

    p_next = sub.add_parser("next", help="print only the next command")
    _add_json_flag(p_next)

    p_run = sub.add_parser("run", help="print the first executable spine command")

    p_prime = sub.add_parser("prime", help="agent sit-down: doctor then next as JSON")
    p_prime.add_argument("--report-only", action="store_true")

    p_new = sub.add_parser("new", help="mint a work item and/or map ticket")
    p_new.add_argument("kind", nargs="?", choices=["ticket", "work-item"])
    p_new.add_argument("--title", required=True)
    p_new.add_argument("--type", default="grilling")
    p_new.add_argument("--profile", default="software")
    p_new.add_argument("--ticket", action="store_true")
    p_new.add_argument("--work-item", dest="work_item_flag", action="store_true")
    _add_json_flag(p_new)

    p_claim = sub.add_parser("claim")
    p_claim.add_argument("target", nargs="?", help="artifact; omit to claim whatever spine next would claim")
    _add_json_flag(p_claim)

    p_show = sub.add_parser("show", help="print one ticket or work item")
    p_show.add_argument("target")
    _add_json_flag(p_show)
    p_rel = sub.add_parser("release")
    p_rel.add_argument("target")
    _add_json_flag(p_rel)

    p_ss = sub.add_parser("set-status")
    p_ss.add_argument("target")
    p_ss.add_argument("status")
    _add_json_flag(p_ss)

    p_link = sub.add_parser("link")
    p_link.add_argument("a")
    p_link.add_argument("b")
    _add_json_flag(p_link)

    p_doc = sub.add_parser("doctor")
    p_doc.add_argument("--report-only", action="store_true")
    _add_json_flag(p_doc)

    p_wire = sub.add_parser("wire", help="install or record skills.sh craft packs")
    p_wire.add_argument("--install", action="store_true", help="npx skills add default pack")
    p_wire.add_argument("--pack", default="mattpocock/skills")

    sub.add_parser("evolve", help="refresh binder from wheel; update skills.sh installs")

    args = parser.parse_args(argv)
    root = _root()
    as_json = bool(getattr(args, "as_json", False) or getattr(args, "as_json_root", False))

    try:
        if args.cmd is None:
            payload = status_payload(root)
            if as_json:
                print(json.dumps(payload, indent=2))
            else:
                print(board(root), end="")
            return 0
        if args.cmd == "init":
            for line in init_target(root, refresh=args.refresh):
                print(line)
            print()
            print(board(root), end="")
        elif args.cmd == "status":
            payload = status_payload(root)
            if as_json:
                print(json.dumps(payload, indent=2))
            else:
                print(board(root), end="")
        elif args.cmd == "next":
            payload = status_payload(root)
            if as_json:
                print(
                    json.dumps(
                        {
                            "cwd": payload["cwd"],
                            "user": payload["user"],
                            "version": payload["version"],
                            "next": payload["next"],
                            "run": payload["run"],
                            "hitl": payload["hitl"],
                        },
                        indent=2,
                    )
                )
            else:
                for line in payload["next"]:
                    print(line)
        elif args.cmd == "new":
            want_ticket = args.kind == "ticket" or args.ticket
            want_wi = args.kind == "work-item" or args.work_item_flag
            if not want_ticket and not want_wi:
                raise ValueError("new needs ticket and/or work-item")
            minted: list[str] = []
            if want_ticket:
                minted.append(str(new_ticket(root, args.title, args.type)))
            if want_wi:
                minted.append(str(new_work_item(root, args.title, args.profile)))
            _emit_payload_or_next(root, as_json, *minted)
        elif args.cmd == "claim":
            spec = args.target or claimable_from_next(root)
            claimed = claim(root, spec)
            if as_json:
                print(json.dumps(status_payload(root), indent=2))
            else:
                print(claimed)
                print()
                _print_next(root)
        elif args.cmd == "show":
            path = resolve_artifact(root, args.target)
            if as_json:
                meta, body = read_meta(path)
                print(
                    json.dumps(
                        {
                            "file": str(path.relative_to(root)),
                            "meta": meta,
                            "body": body,
                        },
                        indent=2,
                    )
                )
            else:
                print(path.read_text(encoding="utf-8"), end="")
        elif args.cmd == "run":
            payload = status_payload(root)
            run = payload["run"]
            if not run:
                first = (payload["next"] or ["nothing to run"])[0]
                print(f"error: {first}", file=sys.stderr)
                return 2
            step = run[0]
            print(step["cmd"] if isinstance(step, dict) else step)

        elif args.cmd == "release":
            _emit_payload_or_next(root, as_json, str(release(root, args.target)))
        elif args.cmd == "set-status":
            _emit_payload_or_next(
                root, as_json, str(set_status(root, args.target, args.status))
            )
        elif args.cmd == "link":
            link(root, args.a, args.b)
            _emit_payload_or_next(root, as_json, "linked")
        elif args.cmd in {"doctor", "prime"}:
            msgs = doctor(root, apply=not getattr(args, "report_only", False))
            payload = status_payload(root)
            want_json = as_json or args.cmd == "prime"
            if want_json:
                print(
                    json.dumps(
                        {
                            "messages": msgs,
                            "ok": doctor_ok(msgs),
                            "cwd": payload["cwd"],
                            "inited": (root / SPEC_ROOT / "contract.yaml").exists(),
                            "user": payload["user"],
                            "version": payload["version"],
                            "next": payload["next"],
                            "run": payload["run"],
                            "hitl": payload["hitl"],
                        },
                        indent=2,
                    )
                )
            else:
                for line in msgs:
                    print(line)
                print()
                _print_next(root)
            return 0 if doctor_ok(msgs) else 8
        elif args.cmd == "wire":
            set_pack(root, args.pack)
            if args.install:
                for line in install_wires(root, extra_pack=args.pack):
                    print(line)
            else:
                print(f"default_pack={args.pack} (pass --install to run npx skills add)")
        elif args.cmd == "evolve":
            for line in evolve(root):
                print(line)
        else:
            parser.error("unknown command")
            return 2
    except SpineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exit_code_for(exc)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exit_code_for(exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
