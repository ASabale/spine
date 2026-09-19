from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spine import __version__
from spine.artifacts import board, claim, link, new_ticket, new_work_item, release, set_status
from spine.doctor import doctor
from spine.evolve import evolve, install_wires, set_pack
from spine.initcmd import init_target


def _root() -> Path:
    return Path.cwd()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spine", description="Harness-agnostic process spine")
    parser.add_argument("--version", action="version", version=f"spine {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="scaffold a target")
    p_init.add_argument("--refresh", action="store_true")

    sub.add_parser("status", help="board")

    p_new = sub.add_parser("new", help="mint a work item and/or map ticket")
    p_new.add_argument("kind", nargs="?", choices=["ticket", "work-item"])
    p_new.add_argument("--title", required=True)
    p_new.add_argument("--type", default="grilling")
    p_new.add_argument("--profile", default="software")
    p_new.add_argument("--ticket", action="store_true")
    p_new.add_argument("--work-item", dest="work_item_flag", action="store_true")

    p_claim = sub.add_parser("claim")
    p_claim.add_argument("target")
    p_rel = sub.add_parser("release")
    p_rel.add_argument("target")

    p_ss = sub.add_parser("set-status")
    p_ss.add_argument("target")
    p_ss.add_argument("status")

    p_link = sub.add_parser("link")
    p_link.add_argument("a")
    p_link.add_argument("b")

    p_doc = sub.add_parser("doctor")
    p_doc.add_argument("--report-only", action="store_true")

    p_wire = sub.add_parser("wire", help="install or record skills.sh craft packs")
    p_wire.add_argument("--install", action="store_true", help="npx skills add default pack")
    p_wire.add_argument("--pack", default="mattpocock/skills")

    sub.add_parser("evolve", help="refresh binder from wheel; update skills.sh installs")

    args = parser.parse_args(argv)
    root = _root()

    try:
        if args.cmd == "init":
            for line in init_target(root, refresh=args.refresh):
                print(line)
        elif args.cmd == "status":
            print(board(root), end="")
        elif args.cmd == "new":
            want_ticket = args.kind == "ticket" or args.ticket
            want_wi = args.kind == "work-item" or args.work_item_flag
            if not want_ticket and not want_wi:
                raise ValueError("new needs ticket and/or work-item")
            if want_ticket:
                print(new_ticket(root, args.title, args.type))
            if want_wi:
                print(new_work_item(root, args.title, args.profile))
        elif args.cmd == "claim":
            print(claim(root, args.target))
        elif args.cmd == "release":
            print(release(root, args.target))
        elif args.cmd == "set-status":
            print(set_status(root, args.target, args.status))
        elif args.cmd == "link":
            link(root, args.a, args.b)
            print("linked")
        elif args.cmd == "doctor":
            for line in doctor(root, apply=not args.report_only):
                print(line)
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
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
