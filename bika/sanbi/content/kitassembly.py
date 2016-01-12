from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi import config
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
import sys
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.sanbi.interfaces import IKitAssembly

schema = BikaSchema.copy() + Schema((
    StringField(
        'KitID',
        searchable=True,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            visible=True,
            label=_("Stock item ID"),
        )
    ),
    ReferenceField('KitTemplate',
        required=1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types=('KitTemplate',),
        relationship='KitAssemblyTemplate',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label = _("Kit template"),
            catalog_name='bika_setup_catalog',
            showOn=False,
            description=_("Start typing to filter the list of available kit templates."),
        ),
    ),
    IntegerField('quantity',
        widget = IntegerWidget(
            label=_("Quantity"),
            description=_("The number of items of this product already in "
                          "storage. eg. 15, 100"),
        ),
    ),
    StringField('location',
        widget = StringWidget(
            label=_("Location"),
        )
    ),
    BooleanField(
        'IsStored',
        default=False,
        widget=BooleanWidget(visible=False),
    ),
))
schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class KitAssembly(BaseContent):
    security = ClassSecurityInfo()
    implements(IKitAssembly)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getKitId(self):
        return self.getId()

    def getKitTemplateTitle(self):
        return self.getKitTemplate().Title()

registerType(KitAssembly, config.PROJECTNAME)
