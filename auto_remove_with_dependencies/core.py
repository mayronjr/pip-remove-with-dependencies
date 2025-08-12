# auto_remove_with_dependencies/__main__.py
from .constants import BLOCKED_PACKAGES

import subprocess

from importlib.metadata import Distribution, distributions
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

def print_verbose(*values, verbose:bool=False):
    if verbose:
        print(*values)

def get_installed_distributions() -> dict[str, tuple[set[str], set[str]]]:
    dists_raw = {
        canonicalize_name(dist.metadata['Name']): dist.requires or []
        for dist in distributions()
        if 'Name' in dist.metadata
    }
    dists = {
        dist_name: {
            canonicalize_name(Requirement(req).name)
            for req in reqs
        }.intersection(dists_raw.keys()) - {dist_name}
        for dist_name, reqs in dists_raw.items()
    }
    new_dists = {}
    for modulo, requeriments in dists.items():
        dependentes = {
            m
            for m, r in dists.items()
            if modulo in r
        }
        new_dists[modulo] = (requeriments, dependentes)
    return new_dists

def find_depenencies_to_uninstall(targets: list, verbose:bool=False):
    dists_dict = get_installed_distributions()
    packs_to_delete = []
    packs_to_validate = [t for t in targets]
    packs_already_validated = set()
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
        requirements = dists_dict[pack][0]
        if len(requirements) != 0:
            print_verbose(f"  Found the following requirements:", ", ".join(requirements), verbose=verbose)
            print_verbose(f"  Adding them to the validation List", verbose=verbose)
        packs_to_validate += (requirements - set(packs_to_validate) - packs_already_validated)
        packs_to_delete.append(pack)
        packs_already_validated.add(pack)
    packs_to_delete = list(set(packs_to_delete))
    packs_to_delete.sort(key=lambda x: len(dists_dict[x][0]), reverse=True)
    print_verbose(f"The following modules have been picked for uninstaling: {', '.join(packs_to_delete)}", verbose=verbose)
    print_verbose("Dependencies analysed. Verifying what can be uninstalled.", verbose=verbose)
    packs_to_delete_validated = list()
    for pack in packs_to_delete:
        dependentes = dists_dict[pack][1]
        if len(dependentes) == 0 or len(dependentes - set(packs_to_delete_validated) - set(packs_to_delete)) == 0:
            packs_to_delete_validated.append(pack)
    
    packs_not_delete = list(set(packs_to_delete) - set(packs_to_delete_validated))
    packs_not_delete.sort(key=lambda x: len(dists_dict[x][0]), reverse=True)
    for pack in packs_not_delete:
        print_verbose(f"> The module {pack} can not be uninstalled because it is required by modules that wont be uninstalled: {', '.join(dists_dict[pack][1]-set(packs_to_delete_validated))}", verbose=verbose)
    packs_to_delete_validated.sort(key=lambda x: len(dists_dict[x][0]), reverse=True)
    return packs_to_delete_validated

def uninstall_packages(packages: list[str], commit:bool):
    if not packages:
        print(f"No modules to uninstall.")
        return
    if not commit:
        print(f"[Dry run] To delete, use --commit")
        print(f"[Dry run] Would uninstall: {', '.join(packages)}")
    else:
        subprocess.run(["pip", "uninstall", "-y", *packages], check=True)
