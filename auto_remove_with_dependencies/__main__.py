from .constants import BLOCKED_PACKAGES
from .core import find_depenencies_to_uninstall, uninstall_packages

import argparse
from . import __version__

def autoremove(target_packages: list[str], commit:bool=False, verbose:bool=False):
    target_packages = [p.lower() for p in target_packages]
    if set(target_packages).intersection(BLOCKED_PACKAGES):
        raise Exception(f"Cant uninstall the following packages: {', '.join(set(target_packages).intersection(BLOCKED_PACKAGES))}")
    uninstall = find_depenencies_to_uninstall(target_packages, verbose)
    uninstall_packages(uninstall, commit)

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to remove packages with dependencies that are unused by other modules."
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando uninstall
    uninstall_parser = subparsers.add_parser(
        "uninstall", help="Uninstall a package and its dependencies that are unused by other modules."
    )
    uninstall_parser.add_argument(
        "packages", nargs="+", help="Target packages to uninstall."
    )
    uninstall_parser.add_argument(
        "--commit", action="store_true",
        help="Actually uninstall. If omitted, just shows what would be removed."
    )
    uninstall_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Show detailed execution output."
    )

    args = parser.parse_args()

    if args.command == "uninstall":
        autoremove(args.packages, commit=args.commit, verbose=args.verbose)
        
if __name__ == "__main__":
    main()