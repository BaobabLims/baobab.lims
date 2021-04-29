# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import ReferenceField, registerType
from plone import api
from plone.app.folder.folder import ATFolder
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.public import Schema
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IFreezer
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.content.bikaschema import BikaFolderSchema


StorageUnit = ReferenceField(
    'StorageUnit',
    allowed_types=('StorageUnit',),
    relationship='FreezerStorageUnit',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Storage Unit"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select storage unit associated this freezer."),
    )
)

MonitoringDevice = ReferenceField(
    'MonitoringDevice',
    allowed_types=('MonitoringDevice',),
    relationship='FreezerMonitoringDevice',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Current Monitoring Device"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select current monitoring device for this freezer."),
    )
)

schema = BikaFolderSchema.copy() + Schema((
    StorageUnit,
    MonitoringDevice,
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class Freezer(ATFolder):
    security = ClassSecurityInfo()
    implements(IFreezer, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getCurrentTemperature(self):
        brains = api.content.find(self, sort_on='modified',
                portal_type='DeviceReading', sort_order='descending')
        if brains:
            obj = brains[-1].getObject()
            current_reading = obj.getCurrentReading()
            unit = obj.getUnit()
            record_date = obj.getDatetimeRecorded()
            return '{} {} at {}'.format(current_reading, unit, record_date)
        return ''

    def getMonitoringDeviceUID(self):
        return self.getMonitoringDevice().UID()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
registerType(Freezer, config.PROJECTNAME)
