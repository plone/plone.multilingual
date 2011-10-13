from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='plone.multilingual',
      version=version,
      description="Multilingual Core",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Ramon Navarro Bosch',
      author_email='ramon@.nb@gmail.com',
      url='http://github.com/bloodbare/plone.multilingual/',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.intid',
          'plone.app.intid'
      ],
      extras_require={
          'test': ['plone.app.testing', ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
