# setup.py
from setuptools import setup, find_packages

setup(
    name="autoremove",
    version="0.1.1",
    author="Mayron Moura Soares Junior",
    author_email="mayronjunior5@gmail.com",
    description="A pip auxiliar that uninstall the packages passed and its unused dependencies.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="No git yet",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "autoremove = autoremove.__main__:main"
        ]
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        # "License :: OSI Approved :: MIT License",  # or other license
        "Operating System :: OS Independent",
    ],
)
