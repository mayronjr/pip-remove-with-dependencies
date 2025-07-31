import subprocess
import pkg_resources

BLOCKED_PACKAGES = {'pip', 'setuptools'}


def get_installed_distributions() -> dict[str, pkg_resources.DistInfoDistribution]:
    return {
        dist.project_name.lower(): dist
        for dist in pkg_resources.working_set
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
    # print('Delete: ', packs_to_delete)
    
    return [pack for (pack, _) in packs_to_delete]

def uninstall_packages(packages):
    if not packages:
        print("No packages to uninstall.")
        return
    print(f"Uninstalling: {', '.join(packages)}")
    subprocess.run(["pip", "uninstall", "-y", *packages], check=True)

def autoremove(target_packages: str):
    target_packages = [p.lower() for p in target_packages]
    if set(target_packages).intersection(BLOCKED_PACKAGES):
        raise Exception(f"Cant uninstall the following packages: {', '.join(set(target_packages).intersection(BLOCKED_PACKAGES))}")
    uninstall = find_depenencies_to_uninstall(target_packages)
    uninstall_packages(uninstall)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python autoremove.py <package1> [package2 ...]")
        sys.exit(1)
    autoremove(sys.argv[1:])
