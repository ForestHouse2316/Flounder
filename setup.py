from setuptools import setup
from flounder import flounder

setup(name='mermaid-flounder',
      version=flounder.VER,
      description='Automation tools for Mermaid diagram',
      author='ForestHouse',
      author_email='foresthouse2316@gmail.com',
      url='https://github.com/ForestHouse2316/flounder',
      license='MIT',
      py_modules=['flounder'],
      python_requires='>=3',
      install_requires=[],
      packages=['flounder']
      )
