"""Command line tool for SMFR validation and comparison."""
import argparse
import json
from dataclasses import asdict
from .core import parse, compare, IncomparableVersions


def main() -> int:
    parser = argparse.ArgumentParser(prog="smfr")
    cmds = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "parse"):
        cmds.add_parser(name).add_argument("version")
    comparison = cmds.add_parser("compare")
    comparison.add_argument("left")
    comparison.add_argument("right")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            version = parse(args.version)
            print("VALID")
            for warning in version.warnings:
                print(f"WARNING: {warning}")
        elif args.command == "parse":
            version = parse(args.version)
            print(json.dumps({**asdict(version), "warnings": version.warnings}, indent=2))
        else:
            result = compare(args.left, args.right)
            print("EQUAL" if result == 0 else "LESS" if result < 0 else "GREATER")
    except IncomparableVersions as exc:
        print(f"INCOMPARABLE: {exc}")
        return 2
    except ValueError as exc:
        print(f"INVALID: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
