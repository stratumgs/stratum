from setuptools import setup, find_packages

import stratumgs


def readme():
      with open('README.rst') as f:
            return f.read()


setup(name='stratumgs',
      version=stratumgs.version,
      description='A turn based game engine designed to pit autonomous players against each other.',
      long_description=readme(),
      keywords=['stratumgs'],
      url='https://github.com/stratumgs/stratumgs',
      author='David Korhumel',
      author_email='dpk2442@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['tornado'],
      include_package_data=True,
      zip_safe=False)
