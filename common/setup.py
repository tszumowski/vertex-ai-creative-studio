from setuptools import find_packages, setup

setup(
    name="creative-studio-common-utils",  # Choose a name for your package
    version="0.1.0",
    packages=find_packages(),
    install_requires=open("requirements.txt").readlines(),
)
