# setup.py
from setuptools import setup, find_packages

setup(
    name="auto_remove_with_dependencies",
    version="0.3.1",
    author="Mayron Moura Soares Junior",
    license="MIT",
    author_email="mayronjunior5@gmail.com",
    description="A pip auxiliar that uninstall the packages passed and its unused dependencies.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mayronjr/pip-remove-with-dependencies",
    packages=find_packages(),
    install_requires=[
        "packaging>=20.0",
    ],
    entry_points={
        "console_scripts": [
            "auto_remove = auto_remove_with_dependencies.__main__:main"
        ]
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",  # or other license
        "Operating System :: OS Independent",
    ],
)
