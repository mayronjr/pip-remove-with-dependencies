# auto_remove_with_dependencies/__main__.py
from .constants import BLOCKED_PACKAGES

import subprocess

from importlib.metadata import Distribution, distributions
from packaging.requirements import Requirement

def print_verbose(*values, verbose:bool=False):
    if verbose:
        print(*values)

def get_installed_distributions() -> dict[str, Distribution]:
    return {
        dist.metadata['Name'].lower(): dist
        for dist in distributions()
        if 'Name' in dist.metadata
    }

def get_dependencies(dist: Distribution) -> set[str]:
    requires = dist.requires or []
    return {
        Requirement(r).name.lower()
        for r in requires
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
