# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.Archetypes.public import Schema
from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import registerType
from Products.CMFPlone.interfaces import IConstrainTypes
from plone.app.folder.folder import ATFolder
from zope.interface import implements

from bika.lims.content.bikaschema import BikaFolderSchema
from baobab.lims.interfaces import IMonitoringDevice
from baobab.lims import config

schema = BikaFolderSchema.copy() + Schema((

))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class MonitoringDevice(ATFolder):
    security = ClassSecurityInfo()
    implements(IMonitoringDevice, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
registerType(MonitoringDevice, config.PROJECTNAME)
