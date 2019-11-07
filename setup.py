from setuptools import setup, find_packages
import os

version = '1.3'

setup(name='baobab.lims',
      version=version,
      description="Starting point for creating Bika LIMS extension packages",
      long_description=open("README.md").read(),
      # Get more strings from ...
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
      namespace_packages=['baobab'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'bika.lims',
          'archetypes.schemaextender',
          'plone.app.relationfield',
          'z3c.relationfield',
          'collective.wtf',
          'plone.formwidget.datetime',
          'plone.app.jquery = 1.11.2',
          'plone.app.jquerytools = 1.7.0',
          'collective.js.bootstrap = 3.3.5',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'robotsuite',
              'robotframework-selenium2library',
              'plone.app.robotframework',
              'Products.PloneTestCase',
              'robotframework-debuglibrary',
              'plone.resource',
              'plone.app.textfield',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
