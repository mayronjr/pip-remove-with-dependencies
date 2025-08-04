# autoremove/__main__.py

import subprocess
import pkg_resources
import argparse

BLOCKED_PACKAGES = {'pip', 'setuptools', 'autoremove'}


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

def find_depenencies_to_uninstall(targets: list):
    dists_dict = get_installed_distributions()
    packs_to_delete = []
    packs_to_validate = [t for t in targets]
    while packs_to_validate:
        pack = packs_to_validate.pop()
        if pack in BLOCKED_PACKAGES:
            print(f"Skipping Uninstall of Module {pack} because its protected.")
            continue
        if pack not in dists_dict.keys():
            print(f"Skipping Uninstall of Module {pack} because its not installed.")
            continue
        dist = dists_dict[pack]
        dependencies = get_dependencies(dist)
        packs_to_validate += dependencies
        packs_to_delete.append((pack, dependencies))
    packs_not_to_delete = {
        dep
        for p, k in dists_dict.items()
        if p not in [pack[0] for pack in packs_to_delete]
        for dep in get_dependencies(k)
    }
    packs_to_delete = [
        i
        for i in packs_to_delete
        if i[0] not in packs_not_to_delete
    ]
    
    return [pack for (pack, _) in packs_to_delete]

def uninstall_packages(packages: list[str], commit:bool):
    if not packages:
        return
    if not commit:
        print(f"[Dry run] To delete, use --commit")
        print(f"[Dry run] Would uninstall: {', '.join(packages)}")
    else:
        subprocess.run(["pip", "uninstall", "-y", *packages], check=True)


def autoremove(target_packages: list[str], commit:bool=False):
    target_packages = [p.lower() for p in target_packages]
    if set(target_packages).intersection(BLOCKED_PACKAGES):
        raise Exception(f"Cant uninstall the following packages: {', '.join(set(target_packages).intersection(BLOCKED_PACKAGES))}")
    uninstall = find_depenencies_to_uninstall(target_packages)
    uninstall_packages(uninstall, commit)

def main():
    parser = argparse.ArgumentParser(description="Autoremove Python packages and its unused dependencies.")
    parser.add_argument("packages", nargs="+", help="Target packages to uninstall.")
    parser.add_argument("--commit", action="store_true", help="Only show what would be uninstalled.")
    args = parser.parse_args()

    autoremove(args.packages, commit=args.commit)

if __name__ == "__main__":
    main()