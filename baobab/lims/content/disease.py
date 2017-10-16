from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IDisease

# DiseaseOntology = StringField(
#         'DiseaseOntology',
#         required=1,
#         searchable=True,
#         read_permission=permissions.View,
#         write_permission=permissions.ModifyPortalContent,
#         widget=StringWidget(
#             label=_("Disease Ontology"),
#             description=_("Disease ontology."),
#             visible={'edit': 'visible',
#                      'view': 'visible'},
#         )
#     )

OntologyVersion = StringField(
        'OntologyVersion',
        required=0,
        searchable=True,
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Ontology Version"),
            description=_("Disease ontology version."),
            visible={'edit': 'visible',
                     'view': 'visible'},
        )
    )

OntologyCode = StringField(
        'OntologyCode',
        required=0,
        searchable=True,
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Ontology Code"),
            description=_("Code for ontology version."),
            visible={'edit': 'visible',
                     'view': 'visible'},
        )
    )

# OntologyDescription = TextField(
#         'OntologyDescription',
#         required=0,
#         searchable=True,
#         allowable_content_types=('text/plain',),
#         default_output_type="text/plain",
#         mode="rw",
#         read_permission=permissions.View,
#         write_permission=permissions.ModifyPortalContent,
#         widget=TextAreaWidget(
#             label=_("Ontology Description"),
#             description=_("Description of the ontology."),
#         )
#     )


DiseaseFree = TextField(
        'DiseaseFree',
        required=0,
        #searchable=True,
        allowable_content_types=('text/plain',),
        default_output_type="text/plain",
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=TextAreaWidget(
            label=_("Disease Free Description"),
            description=_("Explanation of disease or symptom if disease unknown or insufficient information exists."),
        )
    )

schema = BikaSchema.copy() + Schema((
    #DiseaseID,
    #DiseaseOntology,
    OntologyVersion,
    OntologyCode,
    #OntologyDescription,
    DiseaseFree
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}


class Disease(BaseContent):
    security = ClassSecurityInfo()
    implements(IDisease, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # def getTitle(self):
    #     return self.getDiseaseOntology()

registerType(Disease, config.PROJECTNAME)