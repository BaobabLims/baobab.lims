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
from baobab.lims.interfaces import IHostDisease
from Products.Archetypes.public import BaseContent

schema = BikaSchema.copy() + Schema((

))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True



class HostDisease(BaseContent):
    security = ClassSecurityInfo()
    implements(IHostDisease, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)
    #
    # def Title(self):
    #     return safe_unicode(self.getField('SampleDonorID').get(self)).encode('utf-8')
    #
    # def Description(self):
    #     return "Gender %s : Age %s %s" % (self.getSex(), self.getAge(), self.getAgeUnit())
    #
    # def getSexes(self):
    #     return ['Male', 'Female', 'Unknown', 'Undifferentiated']
    #
    # def getAgeUnits(self):
    #     return ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes']

registerType(HostDisease, config.PROJECTNAME)