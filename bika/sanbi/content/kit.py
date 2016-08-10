from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi import config
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
import sys
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.sanbi.interfaces import IKit, IKitStorage
from Products.CMFPlone.interfaces import IConstrainTypes

from Products.CMFCore import permissions
from plone.indexer import indexer


@indexer(IKit)
def get_kit_project_uid(instance):
    return instance.getProject().UID()

schema = BikaSchema.copy() + Schema((
    ReferenceField(
        'Project',
        required=1,
        vocabulary_display_path_bound=sys.maxint,
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
                       catalog_name='bika_setup_catalog',
                       showOn=True,
                       description=_("Start typing to filter the list of available kit templates."),
                   )
                   ),
    ReferenceField(
        'StorageLocation',
        allowed_types=('UnmanagedStorage', 'StoragePosition'),
        relationship='ItemStorageLocation',
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
                        'object_provides': IKitStorage.__identifier__},
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'id', 'width': '30', 'label': _('ID')},
                      {'columnName': 'Title', 'width': '50', 'label': _('Title')},
                      ],
        )),

    BooleanField(
        'IsStored',
        default=False,
        widget=BooleanWidget(visible=False),
    ),

    ReferenceField(
        'Attachment',
        multiValued=1,
        allowed_types=('Attachment',),
        referenceClass=HoldingReference,
        relationship='KitAttachment',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ComputedWidget(
            visible={'edit': 'invisible',
                     'view': 'invisible',
                     },
        )
    ),

    BooleanField(
        'FormsThere',
        required=1,
        default=False,
        widget=BooleanWidget(
            label="Form Added to Kit",
            description="It is necessary to add all forms describing the content of the kit.",
            visible={'edit': 'visible', 'view': 'visible'}
        )
    ),
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class Kit(BaseContent):
    security = ClassSecurityInfo()
    implements(IKit, IConstrainTypes)
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(Kit, config.PROJECTNAME)
