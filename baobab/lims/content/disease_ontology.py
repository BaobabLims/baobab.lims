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
        description=_("Version of selected ontology for disease e.g. ICD-9, ICD-10, SNOMED-CT"),
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
        description=_("Disease code from the selected Disease Ontology Version e.g. C61"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

remarks = StringField(
    'FreeText',
    widget=TextAreaWidget(
        label=_("Remarks"),
        description=_("Explanation about disease or symptom in case of unknown disease or insufficient information"),
        cols=30,
        rows=20,
    ),
)

schema = BikaSchema.copy() + Schema((
    version,
    code,
    remarks
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['title'].widget.label = "Disease Ontology"
schema['title'].widget.description = "Name of ontology used fro disease. Can be several values e.g. ICD, SNOMED"
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.description = "Description from the selected Disease Ontology Code " \
                                           "e.g. Malignant neoplasm of prostate"


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