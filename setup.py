# setup.py
from setuptools import setup, find_packages

setup(
    name="autoremove",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "autoremove = autoremove.__main__:main"
        ]
    },
)
