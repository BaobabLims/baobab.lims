# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl.SecurityInfo import ClassSecurityInfo
# from Products.Archetypes.public import BaseFolder
# from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import Schema
from Products.Archetypes.public import registerType
# from Products.CMFCore.utils import getToolByName
# from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import implements
from baobab.lims import config
# from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.interfaces import IConstrainTypes
from baobab.lims.interfaces import ICollectionDevice
from Products.Archetypes.public import BaseContent

schema = BikaSchema.copy() + Schema((

))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True



class CollectionDevice(BaseContent):
    security = ClassSecurityInfo()
    implements(ICollectionDevice, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(CollectionDevice, config.PROJECTNAME)
