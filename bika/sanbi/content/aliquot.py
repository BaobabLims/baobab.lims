from Products.Archetypes.public import *
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.references import HoldingReference
from bika.sanbi import bikaMessageFactory as _
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from bika.sanbi.interfaces import IAliquot
from bika.sanbi import config
import sys
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFCore import permissions

schema = BikaSchema.copy() + Schema((
    ReferenceField(
        'Biospecimen',
        required=1,
        allowed_types=('Biospecimen',),
        relationship='BiospecimenAliquot',
        vocabulary_display_path_bound=sys.maxsize,
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
           checkbox_bound=0,
           label=_("Biospecimen"),
           description=_("Select the biospecimen from the aliquot is extracted."),
           size=40,
           catalog_name='bika_setup_catalog',
           showOn=True,
           visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    FixedPointField(
        'Volume',
        required=1,
        default="0.00",
        widget=DecimalWidget(
            label=_("Volume"),
            size=15,
            description=_("The volume of the sample taken from the biospecimen."),
        )
    ),

    StringField(
        'Unit',
        widget=StringWidget(
            label=_("Unit"),
            visible={'edit': 'visible', 'view': 'visible'}
        )
    ),

    ReferenceField(
        'AliquotType',
        allowed_types=('AliquotType',),
        relationship='AliquotTypeAliquot',
        vocabulary_display_path_bound=sys.maxsize,
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
           checkbox_bound=0,
           label=_("Aliquot Type"),
           description=_("Select the type of the sample."),
           size=40,
           catalog_name='bika_setup_catalog',
           showOn=True,
           visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    ReferenceField(
        'StorageLocation',
        allowed_types=('StorageLocation',),
        relationship='AliquotStorageLocation',
        widget=bika_ReferenceWidget(
            label=_("Storage Location"),
            description=_("Location where sample is kept"),
            size=40,
            visible={'edit': 'visible', 'view': 'visible'},
            catalog_name='bika_setup_catalog',
            showOn=True,
            base_query={'inactive_state': 'active', 'review_state': 'available'},
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Room', 'width': '15', 'label': _('Room')},
                      {'columnName': 'StorageType', 'width': '15', 'label': _('Type')},
                      {'columnName': 'Shelf', 'width': '13', 'label': _('Sh./Ca.')},
                      {'columnName': 'Box', 'width': '13', 'label': _('Box/Cane')},
                      {'columnName': 'Position', 'width': '13', 'label': _('Pos.')},
                      {'columnName': 'Title', 'width': '31', 'label': _('Address')},
                      ],
        ),
    ),
))

schema['title'].required = True
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'edit': 'visible', 'view': 'visible'}

class Aliquot(BaseContent):
    implements(IAliquot)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def guard_store_transition(self):
        """Return True if object's storage location is referenced and the actual state
           is pending. This will show a button "store sample" and allow a transition
           to "Store" state.
        """
        return True

    def guard_pending_transition(self):
        """Return true if object reference to any storage location and it's actual state
           'store'. In this case we have to change state a button will be shown and allow
           a transition to 'pending' state.
        """
        return True


registerType(Aliquot, config.PROJECTNAME)
