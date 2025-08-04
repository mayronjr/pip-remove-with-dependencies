# auto_remove_with_dependencies

A CLI tool that removes a Python package along with all of its unused dependencies.

Useful when you want to clean up after uninstalling something like `pandas`, and don't want to leave `numpy`, `tzdata`, and other unused packages behind.

# How to use

After installing it, you can use it as ```auto_remove uninstall modules*```.

You can pass any amount of modules that you want. It will analyse all of them.

To not delete your entire enviroment, the CLI client only execute the modifications if you provide the arg ```--commit```. If it is ommited, it will only show what modules would be uninstalled.