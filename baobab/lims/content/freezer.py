# -*- coding: utf-8 -*-

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import ReferenceField, registerType
from plone import api
from plone.app.folder.folder import ATFolder
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.public import Schema
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFCore.utils import getToolByName
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

    def getLatestTemperature(self):
        bc = getToolByName(self, 'bika_catalog')
        # Get the last temperature recorded
        limit = 1
        brains = bc(portal_type='DeviceReading',
                    path={'query': "/".join(self.getPhysicalPath())},
                    sort_on='getDatetimeRecorded',
                    sort_order='descending',
                    sort_limit=limit)[:limit]

        if not brains:
            return ''

        obj = brains[0].getObject()
        current_reading = obj.getCurrentReading()
        unit = obj.getUnit()
        record_date = obj.getDatetimeRecorded()
        if obj.getDatetimeRecorded and current_reading:
            return '{} {} at {}'.format(current_reading, unit, record_date)
        return ''

    def getMonitoringDeviceUID(self):
        return self.getMonitoringDevice().UID()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
registerType(Freezer, config.PROJECTNAME)
