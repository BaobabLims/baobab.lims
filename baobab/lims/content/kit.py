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
from baobab.lims.interfaces import IKit, IKitStorage


Project = ReferenceField(
    'Project',
    required=1,
    allowed_types=('Project',),
    relationship='KitProject',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Project"),
        catalog_name='bika_catalog',
        size=30,
        showOn=True,
        description=_("Click and select project for the kit."),
    )
)

KitTemplate = ReferenceField(
    'KitTemplate',
    required=0,
    allowed_types=('KitTemplate',),
    relationship='KitAssemblyTemplate',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Kit template"),
        size=30,
        catalog_name='bika_setup_catalog',
        showOn=True,
        description=_(
            "Start typing to filter the list of available kit "
            "templates."),
    )
)

StorageLocation = ReferenceField(
    'StorageLocation',
    allowed_types=('UnmanagedStorage', 'StoragePosition'),
    relationship='ItemStorageLocation',
    widget=bika_ReferenceWidget(
        label=_("Storage Location"),
        description=_("Location where item is kept"),
        size=40,
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='portal_catalog',
        showOn=True,
        base_query={'inactive_state': 'active',
                    'review_state': 'available',
                    'object_provides': IKitStorage.__identifier__},
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'id', 'width': '30', 'label': _('ID')},
                  {'columnName': 'Title', 'width': '50',
                   'label': _('Title')},
                  ],
    )
)

StockItems = ReferenceField(
    'StockItems',
    multiValued=1,
    allowed_types=('StockItem',),
    relationship='KitStockItem',
    widget=ComputedWidget(
        visible={'edit': 'invisible',
                 'view': 'invisible',
                 },
    )
)

Attachment = ReferenceField(
    'Attachment',
    multiValued=1,
    allowed_types=('Attachment',),
    referenceClass=HoldingReference,
    relationship='KitAttachment',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ComputedWidget(
        visible={'edit': 'invisible', 'view': 'invisible'},
    )
)

FormsThere = BooleanField(
    'FormsThere',
    required=1,
    default=False,
    widget=BooleanWidget(
        label="Form Added to Kit",
        description="It is necessary to add all forms describing the content "
                    "of the kit.",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

DateCreated = DateTimeField(
    'DateCreated',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Created"),
        visible={'edit': 'invisible', 'view': 'invisible'},
    ),
)

schema = BikaSchema.copy() + Schema((
    Project,
    KitTemplate,
    StorageLocation,
    StockItems,
    Attachment,
    FormsThere,
    DateCreated
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}


class Kit(BaseContent):
    security = ClassSecurityInfo()
    implements(IKit, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getParentUID(self):
        return self.aq_parent.UID()

registerType(Kit, config.PROJECTNAME)
