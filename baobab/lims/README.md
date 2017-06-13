Introduction
============

Code for baobab.lims is rooted in this folder.

The root of all configuration is the configure.zcml file.  Reading this file
is the quickest way to discover what's available in the system, which URLs
are mapped to which views, and which adapters have been configured.

overrides.zcml performs the same task, but handles the case where a zcml
directive is identical to one in the base bika.lims package.  In this case,
adding the directive in a normal zcml file will result in a configuration
error.  The root overrides.zcml is reponsible for including all other
overrides in this package.

Items in this folder
====================

- adapters/

    Customisations to bika.lims adapters.  Adapters can be located anywhere
    in the system, making them possibly quite hard to discover unless they
    are documented.  I prefer to keep them located here, inside packages
    named after their function, especially if they are general-purpose adapters
    which can be applied to more than one content type.  It's perfectly OK to
    splatter them around the source in any way you like, though.
    
- browser/

    Contains browser views, both new ones and those which are subclassed
    from the base bika.lims package and overriden in overrides.zcml.
 
- content/

    Any new content types (AT or Dexterity classes) should be created in this
    folder.  Read the Plone docs for information on creating new AT or 
    Dexterity objects; nothing special here.

- extenders/

    This folder contains all schemaextender Extender and Modifier classes.

- locales/

    Contains all translations for this package, for both new strings and for
    strings which are "renamed" or overridden from the base package.

- profiles/
 
    This is the "Generic Setup" profile for this package.
 
- reports/

    Custom reports

- setupdata/

    Should contain a dataset with all data required for running this package's
    tests.

- static/

    Static resources for this package (javascript, CSS and images).

- tests/

    Everything should be tested!  This folder contains some basic examples
    of robotframework tests.

- config.py - Constants used in this package.
- configure.zcml - Main configuration begins here
- overrides.zcml - Configure ZCML configuration overrides
- permissions.py - All permissions must exist in the .py and .zcml files
- permissions.zcml - All permissions must exist in the .py and .zcml files
- profiles.zcml - GS Profiles are configured here
- setuphandlers.py - Extra installation/configuration steps
- testing.py - Test layer configuration
