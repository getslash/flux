import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "flux", "__version__.py")) as version_file:
    exec(version_file.read()) # pylint: disable=W0122

setup(name="flux",
      classifiers = [
          "Programming Language :: Python :: 2.7",
          ],
      description="Artificial time library",
      license="BSD",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=__version__, # pylint: disable=E0602
      packages=find_packages(exclude=["tests"]),
      install_requires=[],
      scripts=[],
      namespace_packages=[]
      )
