from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from plone.indexer import indexer

from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.sanbi.interfaces import IAliquot, IAliquotStorage
from bika.sanbi import config
from bika.sanbi import bikaMessageFactory as _

import sys


@indexer(IAliquot)
def project_uid(instance):
    return instance.getBiospecimen().getKit().getProject().UID()

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
           description=_("The biospecimen the aliquot is extracted from."),
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
        allowed_types=('BiospecType'), # It was befor 'AliquotType'
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
        allowed_types=('UnmanagedStorage', 'StoragePosition'),
        relationship='AliquotStorageLocation',
        widget=bika_ReferenceWidget(
            label=_("Storage Location"),
            description=_("Location where item is kept"),
            size=40,
            visible={'edit': 'visible', 'view': 'visible'},
            catalog_name='bika_setup_catalog',
            showOn=True,
            render_own_label=True,
            base_query={'inactive_state': 'active',
                        'review_state': 'available',
                        'object_provides': IAliquotStorage.__identifier__},
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'id', 'width': '30', 'label': _('ID')},
                      {'columnName': 'Title', 'width': '50', 'label': _('Title')},
                      ],
        )
    ),

    DateTimeField(
        'DateCreated',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=DateTimeWidget(
            label=_("Date Created"),
            visible={'edit': 'invisible', 'view': 'invisible'},
        )
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
