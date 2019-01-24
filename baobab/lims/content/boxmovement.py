from AccessControl import ClassSecurityInfo

from bika.lims.browser.widgets import ReferenceWidget as BikaReferenceWidget, SelectionWidget, DateTimeWidget
from bika.lims.browser.fields import ProxyField
from Products.Archetypes.public import ReferenceField, Schema, BaseContent, registerType, StringField, DisplayList, ReferenceWidget as OldRefWidget
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFCore.utils import getToolByName
from plone.indexer import indexer
from zope.interface import implements
from Products.Archetypes.atapi import *

from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.fields import DateTimeField
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config

from baobab.lims.interfaces import IBoxMovement, IKitStorage
from DateTime import DateTime


StorageLocation = ReferenceField(
    'StorageLocation',
    allowed_types=('ManagedStorage'),
    relationship='ItemStorageLocation',
    widget=BikaReferenceWidget(
        label=_("Storage Location"),
        description=_("Location where item is kept"),
        size=40,
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='bika_catalog',
        showOn=True,
        base_query={'inactive_state': 'active', 'getOccupied': False},
        colModel=[
            {'columnName': 'UID', 'hidden': True},
            {'columnName': 'Title', 'width': '20', 'label': _('Title')},
            {"columnName": "Hierarchy", "align": "left", "label": "Hierarchy", "width": "70"},
            {"columnName": "FreePositions", "align": "left", "label": "Free", "width": "10"},
        ],
    )
)

DateCreated = DateTimeField(
    'DateCreated',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        show_time=True,
        label=_("Date Created"),
        visible={'edit': 'visible', 'view': 'visible'},
    ),
)

LabContact = ReferenceField(
    'LabContact',
    required=1,
    allowed_types=('LabContact',),
    referenceClass=HoldingReference,
    relationship='BoxMovementLabContact',
    mode="rw",
    read_permission=permissions.View,
    widget=BikaReferenceWidget(
        label=_("Lab Contact"),
        description=_("Laboratory contact moving the box."),
        size=30,
        base_query={'inactive_state': 'active'},
        showOn=True,
        popup_width='400px',
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'Fullname', 'width': '50', 'label': _('Name')},
                  {'columnName': 'EmailAddress', 'width': '50', 'label': _('Email Address')},
                  ],
    ),
)

NewLocation = ReferenceField(
    'NewLocation',
    allowed_types=('ManagedStorage'),
    relationship='NewLocationItemStorageLocation',
    widget = BikaReferenceWidget(
        label=('New Location'),
        description=_('The New Location where item is to be kept.'),
        size=40,
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='bika_catalog',
        showOn=True,
        base_query={'inactive_state': 'active', 'getOccupied': True},
        colModel=[
             {'columnName': 'UID', 'hidden': True},
             {'columnName': 'Title', 'width': '20', 'label': _('Title')},
             {"columnName": "Hierarchy", "align": "left", "label": "Hierarchy", "width": "70"},
             {"columnName": "FreePositions", "align": "left", "label": "Free", "width": "10"},
        ]
    ),
)


schema = BikaSchema.copy() + Schema((
    StorageLocation,
    DateCreated,
    LabContact,
    NewLocation
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}


class BoxMovement(BaseContent):
    security = ClassSecurityInfo()
    implements(IBoxMovement, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(BoxMovement, config.PROJECTNAME)
