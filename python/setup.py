from setuptools import setup, find_packages

VERSION = "0.0.3"
DESCRIPTION = "EdginAround API"
LONG_DESCRIPTION = "EdginAround API"

setup(
    name="edgin_around_api",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["marshmallow", "marshmallow-enum", "marshmallow-oneofschema"],
)
