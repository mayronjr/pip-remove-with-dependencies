# auto_remove_with_dependencies

A CLI tool that removes a Python package along with all of its unused dependencies. 

Useful when you want to clean up after uninstalling something like `pandas`, and don't want to leave `numpy`, `tzdata`, and other unused packages behind.