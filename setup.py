from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
from Cython.Distutils import build_ext 

py_modules_to_convert = [
    Extension("yaml_illuminate.__init__.py",      ["yaml_illuminate/__init__.py"]),
    Extension("yaml_illuminate.loader",           ["yaml_illuminate/loader.py"]),
    Extension("yaml_illuminate.marked_exception", ["yaml_illuminate/marked_exception.py"]),
    Extension("yaml_illuminate.meta_loader",      ["yaml_illuminate/meta_loader.py"]),
    Extension("yaml_illuminate.objmaker",         ["yaml_illuminate/objmaker.py"])
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yaml_illuminate",
    cmdclass = {'build_ext': build_ext},                     
    version="1.1",
    description="Yaml file loader, with additional metadata, like yaml object location",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ikuksenok",
    url="https://github.com/Kuksenok-i-s/YAML-Illuminate",
    packages=find_packages(
        ["yaml_illuminate"],
        exclude=[
            "__init__.py",
            "loader.py",
            "marked_exception.py",
            "meta_loader.py",
            "objmaker.py"
        ]),
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
    platforms="any",
    ext_modules = cythonize(py_modules_to_convert)
)
