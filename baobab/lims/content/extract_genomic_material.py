from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IExtractGenomicMaterial
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFPlone.utils import safe_unicode


VirusSample = ReferenceField(
    'VirusSample',
    allowed_types=('VirusSample',),
    relationship='ExtractGenomicMaterialVirusSample',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Virus Sample"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Virus Sample."),
    )
)

HeatInactivated = BooleanField(
    'HeatInactivated',
    # required=1,
    # schemata='General Info',
    default=False,
    widget=BooleanWidget(
        label="HeatInactivated",
        description="Has this sample been inactivated by heat",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

Method = ReferenceField(
    'Method',
    allowed_types=('Method',),
    relationship='ExtractGenomicMaterialMethod',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Method"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Method."),
    )
)

ExtractionBarcode = StringField(
    'ExtractionBarcode',
    required=1,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Extraction Barcode"),
        description=_("The barcode for the newly extracted genomic material."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Volume = StringField(
    'Volume',
    required=0,
    default='0.0',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DecimalWidget(
        label=_("Volume"),
        description=_("The volume of the newly extracted genomic material."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Unit = StringField(
    'Unit',
    required=0,
    # searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Unit"),
        description=_("The unit of the volume of the newly extracted genomic material."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

WasKitUsed = BooleanField(
    'WasKitUsed',
    # required=1,
    # schemata='General Info',
    default=False,
    widget=BooleanWidget(
        label="Has a Kit been Used",
        description="Indicate if a kit been used to do this extraction.",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

KitNumber = StringField(
    'KitNumber',
    required=0,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Kit Number"),
        description=_("The number of the kit used to create this extraction."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Notes = StringField(
    'Notes',
    required=0,
    # searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Notes"),
        description=_("Any notes related to this genomic extraction."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

schema = BikaSchema.copy() + Schema((
    VirusSample,
    HeatInactivated,
    Method,
    ExtractionBarcode,
    Volume,
    Unit,
    WasKitUsed,
    KitNumber,
    Notes,
))
schema['title'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class ExtractGenomicMaterial(BaseContent):
    security = ClassSecurityInfo()
    implements(IExtractGenomicMaterial, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('ExtractionBarcode').get(self)).encode('utf-8')

registerType(ExtractGenomicMaterial, config.PROJECTNAME)