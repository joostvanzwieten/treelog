from setuptools import setup
import os, re

with open(os.path.join('treelog', '__init__.py')) as f:
  version = next(filter(None, map(re.compile("^version = '([a-zA-Z0-9.]+)'$").match, f))).group(1)

setup(
  name = 'treelog',
  version = version,
  description = 'Logging framework that organizes messages in a tree structure',
  author = 'Evalf',
  author_email = 'info@evalf.com',
  url = 'https://github.com/evalf/treelog',
  packages = ['treelog'],
  license = 'MIT',
  python_requires = '>=3.5',
)
