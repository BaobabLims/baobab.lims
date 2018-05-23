from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IDiseaseOntology


# ontology = StringField(
#     'Ontology',
#     required=1,
#     searchable=True,
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     widget=StringWidget(
#         label=_("Patient ID"),
#         description=_("The unique ID code assigned to the patient."),
#         visible={'edit': 'visible', 'view': 'visible'},
#     )
# )

version = StringField(
    'Version',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Version"),
        description=_("Disease ontology version"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

code = StringField(
    'Code',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Code"),
        description=_("Disease ontology code"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

remarks = TextField(
    'Remarks',
    searchable=True,
    default_content_type='text/x-web-intelligent',
    allowable_content_types=('text/plain', ),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_('Remarks'),
        append_only=True,
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

schema = BikaSchema.copy() + Schema((
    version,
    code,
    remarks
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['title'].widget.label = "Disease Ontology"
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}


class DiseaseOntology(BaseContent):
    security = ClassSecurityInfo()
    implements(IDiseaseOntology, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(DiseaseOntology, config.PROJECTNAME)