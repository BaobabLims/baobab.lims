from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='bika.sanbi',
      version=version,
      description="Starting point for creating Bika LIMS extension packages",
      long_description=open("README.md").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Bika Lab Systems',
      author_email='support@bikalabs.com',
      url='http://www.bikalabs.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'bika.health',
          'archetypes.schemaextender',
          'plone.app.relationfield',
          'z3c.relationfield',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
