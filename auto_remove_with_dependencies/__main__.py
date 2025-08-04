# auto_remove_with_dependencies/__main__.py

import subprocess
import pkg_resources
import argparse
from . import __version__  # importa a versão

BLOCKED_PACKAGES = {'pip', 'setuptools', 'autoremove'}

def print_verbose(*values:object, verbose:bool=False):
    if verbose:
        print(*values)

def get_installed_distributions() -> dict[str, pkg_resources.DistInfoDistribution]:
    working_set = pkg_resources.working_set
    if not working_set or not hasattr(working_set, '__iter__'):
        return {}
    return {
        dist.project_name.lower(): dist
        for dist in list(working_set)
    }

def get_dependencies(dist: pkg_resources.DistInfoDistribution) -> set[str]:
    return {
        dist.project_name.lower()
        for dist in dist.requires()
    }

def find_depenencies_to_uninstall(targets: list, verbose:bool=False):
    dists_dict = get_installed_distributions()
    packs_to_delete = set()
    packs_to_validate = [t for t in targets]
    print_verbose(f"Receive the following list of Modules to uninstall with dependencies:", ', '.join(packs_to_validate), verbose=verbose)
    while packs_to_validate:
        pack = packs_to_validate.pop()
        print_verbose(f"Validating Module {pack}", verbose=verbose)
        if pack in BLOCKED_PACKAGES:
            print_verbose(f"  Skipping Uninstall of Module {pack} because its protected.", verbose=verbose)
            continue
        if pack not in dists_dict.keys():
            if pack in targets:
                print_verbose(f"{' '*2*verbose}Target Module {pack} not installed.", verbose=True)
            else:
                print_verbose(f"  Skipping Uninstall of Module {pack} because its not installed.", verbose=(verbose or pack in targets))
            continue
        dist = dists_dict[pack]
        dependencies = get_dependencies(dist)
        if len(dependencies) != 0:
            print_verbose(f"  Found the following dependencies:", ", ".join(dependencies), verbose=verbose)
            print_verbose(f"  Adding them to the validation List", verbose=verbose)
        packs_to_validate += dependencies
        packs_to_delete.add(pack)
    print_verbose("Dependencies analysed. Verifying what can be uninstalled.", verbose=verbose)
    packs_not_to_delete = {
        dep
        for p, k in dists_dict.items()
        if p not in packs_to_delete
        for dep in get_dependencies(k)
    }
    packs_to_delete_validated = {
        i
        for i in packs_to_delete
        if i not in packs_not_to_delete
    }
    for pack in (packs_to_delete - packs_to_delete_validated):
        dependency_in = {
            p
            for p, k in dists_dict.items()
            if pack in get_dependencies(k)
        }
        print_verbose(f"> The module {pack} can not be uninstalled because it is required by the modules: {', '.join(dependency_in)}", verbose=verbose)
    
    return list(packs_to_delete_validated)

def uninstall_packages(packages: list[str], commit:bool):
    if not packages:
        print(f"No modules to uninstall.")
        return
    if not commit:
        print(f"[Dry run] To delete, use --commit")
        print(f"[Dry run] Would uninstall: {', '.join(packages)}")
    else:
        subprocess.run(["pip", "uninstall", "-y", *packages], check=True)


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
        "--version", "-V",
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