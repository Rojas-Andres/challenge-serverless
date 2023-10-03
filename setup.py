from setuptools import setup

"""
This is a shared_package setup.py script to be used by all modules/functions.
"""
setup(
    name="shared_package",
    packages=["shared_package", "shared_package.db", "shared_package.db.repository", "shared_package.schemas"],
    description="Shared package",
    version="1.0.0",
    author="Andres Rojas",
    author_email="andresfelipe200004@gmail.com",
    keywords=["pip", "shared_package"],
)
