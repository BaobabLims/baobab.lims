from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from plone.indexer import indexer
from zope.interface import implements

from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.fields import DateTimeField
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IBoxMovement, IKitStorage



StorageLocation = ReferenceField(
    'StorageLocation',
    allowed_types=('ManagedStorage'),
    relationship='ItemStorageLocation',
    widget=bika_ReferenceWidget(
        label=_("Storage Location"),
        description=_("Location where item is kept"),
        size=40,
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='portal_catalog',
        showOn=True,
        base_query={'inactive_state': 'active'},
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
    widget=bika_ReferenceWidget(
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
    relationship='NewItemStorageLocation',
    widget=bika_ReferenceWidget(
        label=_("New Location"),
        description=_("The New Location where item is to be kept"),
        size=40,
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='portal_catalog',
        showOn=True,
        base_query={'inactive_state': 'active', 'review_state': 'available'},
        colModel=[
            {'columnName': 'UID', 'hidden': True},
            {'columnName': 'Title', 'width': '20', 'label': _('Title')},
            {"columnName": "Hierarchy", "align": "left", "label": "Hierarchy", "width": "70"},
            {"columnName": "FreePositions", "align": "left", "label": "Free", "width": "10"},
        ],
    )
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
