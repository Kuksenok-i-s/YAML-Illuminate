from setuptools import setup
from Cython.Build import cythonize
from os import walk

# pyx_files = [f"yaml_illuminate/{f}" for _, _, files in walk("yaml_illuminate") for f in files if ".py" in f if "__" not in f]

py_modules_to_convert = [
    # "yaml_illuminate/loader.py",
    "yaml_illuminate/marked_exception.py",
    "yaml_illuminate/meta_loader.py",
    "yaml_illuminate/objmaker.py"
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yaml_illuminate",
    version="1.1",
    description="Yaml file loader, with additional metadata, like yaml object location",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ikuksenok",
    url="https://github.com/Kuksenok-i-s/YAML-Illuminate",
    packages=["yaml_illuminate"],
    install_requires=[
        "PyYAML>=5.4.1",
    ],
    license="GPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    platform="any",
    ext_modules = cythonize(py_modules_to_convert)
)
