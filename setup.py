from setuptools import setup, find_packages

import stratumgs


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='stratumgs',
      version=stratumgs.version,
      description='A turn based game engine designed to pit autonomous players '
                  'against each other.',
      long_description=readme(),
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Environment :: Web Environment',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Topic :: Games/Entertainment :: Board Games',
            'Topic :: Games/Entertainment :: Puzzle Games',
            'Topic :: Games/Entertainment :: Turn Based Strategy'
      ],
      entry_points={
            'console_scripts': ['stratumgs=stratumgs:main']
      },
      keywords=['stratumgs'],
      url='https://stratumgs.org',
      author='David Korhumel',
      author_email='dpk2442@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['tornado'],
      include_package_data=True,
      zip_safe=False)
