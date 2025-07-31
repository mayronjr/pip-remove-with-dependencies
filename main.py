import subprocess
import pkg_resources

def get_installed_distributions() -> dict[str, pkg_resources.DistInfoDistribution]:
    return {dist.project_name.lower(): dist for dist in pkg_resources.working_set}

def get_dependencies(dist: pkg_resources.DistInfoDistribution) -> set[pkg_resources.DistInfoDistribution]:
    try:
        return {str(r).lower() for r in dist.requires()}
    except Exception:
        return {}


def build_dependency_graph() -> dict[str, set[pkg_resources.DistInfoDistribution]]:
    dists = get_installed_distributions()
    graph = {}
    for name, dist in dists.items():
        graph[name] = get_dependencies(dist)
    return graph

def find_unused_dependencies(graph: dict[str, set[pkg_resources.DistInfoDistribution]], targets: list):
    # Start with all dependencies of targets
    dependents = set(targets)
    queue = list(targets)
    while queue:
        current = queue.pop()
        print(dependents)
        for pkg, deps in graph.items():
            if current in deps and pkg not in dependents:
                dependents.add(pkg)
                queue.append(pkg)
    # Unused dependencies are those in dependents minus targets themselves
    print(dependents - set(targets))
    return dependents - set(targets)

def uninstall_packages(packages):
    if not packages:
        print("No packages to uninstall.")
        return
    print(f"Uninstalling: {', '.join(packages)}")
    subprocess.run(["pip", "uninstall", "-y", *packages], check=True)

def autoremove(target_packages: str):
    target_packages = [p.lower() for p in target_packages]
    blocked_packages = {'pip', 'dotenv', 'setuptools', 'python-dotenv'}
    if set(target_packages).intersection(blocked_packages):
        raise Exception(f"Cant uninstall the following packages: {', '.join(set(target_packages).intersection(blocked_packages))}")
    graph = build_dependency_graph()
    unused = find_unused_dependencies(graph, target_packages)
    all_to_remove = set(target_packages) | unused
    # uninstall_packages(list(all_to_remove))

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python autoremove.py <package1> [package2 ...]")
        sys.exit(1)
    autoremove(sys.argv[1:])
