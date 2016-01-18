from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi import config
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
import sys
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.sanbi.interfaces import ISupplyEx

from Products.CMFCore import permissions

schema = BikaSchema.copy() + Schema((
    StringField(
        'KitID',
        searchable=True,
        mode="rw",
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            label=_("Kit ID"),
            size=30,
            render_own_label=True,
            visible={'view': 'visible', 'edit': 'visible'},
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
            size=30,
            render_own_label=True,
            catalog_name='bika_setup_catalog',
            showOn=False,
            description=_("Start typing to filter the list of available kit templates."),
        ),
    ),
    IntegerField('quantity',
        mode="rw",
        widget = IntegerWidget(
            label=_("Quantity"),
            render_own_label=True,
            description=_("The number of kit templates to assemble. eg. 15, 100"),
            visible={'view': 'visible', 'edit': 'visible'},
        ),
    ),
    StringField('location',
        widget = StringWidget(
            label=_("Location"),
            render_own_label=True
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
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.render_own_label = True
schema.moveField('KitID', before='description')
schema.moveField('KitTemplate', before='KitID')

class SupplyEx(BaseContent):
    security = ClassSecurityInfo()
    implements(ISupplyEx)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getKitId(self):
        return self.getId()

    def getKitTemplateTitle(self):
        return self.getKitTemplate().Title()

registerType(SupplyEx, config.PROJECTNAME)
