"""Setup script for the Engine package."""

from setuptools import setup
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="PyStory",
    version="1.2.0",
    author="Alejandro Velázquez",
    author_email="avelazquez@gmail.com",
    description="A text-adventure game engine for creating interactive fiction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LeAle4/Story-Engine",
    # Source files live next to setup.py, so map the package name to "." explicitly.
    packages=["pyStory"],
    package_dir={"pyStory": "."},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Add your dependencies here
        # "PyCLI>=1.0.0",  # Uncomment if PyCLI is available on PyPI
    ],
    extras_require={
    },
    entry_points={
    },
)
