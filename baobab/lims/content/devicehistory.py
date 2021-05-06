from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.public import (
            BaseContent, DateTimeField, ReferenceField, Schema, registerType)
from Products.Archetypes.references import HoldingReference
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.content.bikaschema import BikaSchema
from baobab.lims.interfaces import IDeviceHistory
from baobab.lims import bikaMessageFactory as _
from baobab.lims.config import PROJECTNAME


schema = BikaSchema.copy() + Schema((
    ReferenceField(
        'MonitoringDevice',
        allowed_types=('MonitoringDevice',),
        relationship='DeviceHistoryMonitoringDevice',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label=_("Monitoring Device"),
            visible={'edit': 'visible', 'view': 'visible'},
            size=30,
            showOn=True,
            description=_("Select monitoring device."),
        )
    ),

    ReferenceField(
        'Freezer',
        allowed_types=('Freezer',),
        relationship='DeviceHistoryFreezer',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label=_("Freezer"),
            visible={'edit': 'visible', 'view': 'visible'},
            size=30,
            showOn=True,
            description=_("Select monitoring device."),
        )
    ),

    DateTimeField(
        'DateTimeIn',
        default_method=DateTime,
        widget=CalendarWidget(
            label='Datetime In',
            description='Datetime the device was placed inside the freezer',
            ampm=1,
            visible={'edit': 'visible', 'view': 'visible'}
        )
    ),
    DateTimeField(
        'DateTimeOut',
        default_method=DateTime,
        widget=CalendarWidget(
            label='Datetime out',
            description='Datetime the device was removed from the freezer',
            ampm=1,
            visible={'edit': 'visible', 'view': 'visible'}
        )
    ),
))

schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].schemata = 'default'


class DeviceHistory(BaseContent):
    implements(IDeviceHistory, IConstrainTypes)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema


registerType(DeviceHistory, PROJECTNAME)
