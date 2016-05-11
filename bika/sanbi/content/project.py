from Products.Archetypes.public import *
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.references import HoldingReference
from bika.sanbi import bikaMessageFactory as _
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from bika.sanbi.interfaces import IProject
from bika.sanbi import config
import sys
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget

schema = BikaSchema.copy() + Schema((
    ReferenceField('ClientID',
        required=1,
        allowed_types=('Client',),
        relationship='ClientProject',
        vocabulary_display_path_bound=sys.maxsize,
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            checkbox_bound=0,
            label=_("Client"),
            description=_("Select the project owner."),
            size=30,
            catalog_name='portal_catalog',
            showOn=True,
            visible={'edit': 'visible', 'view': 'visible'},
        )),
    StringField('StudyType',
        searchable=True,
        widget=StringWidget(
            label=_('Type of study'),
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    IntegerField('AgeHigh',
        widget=IntegerWidget(
            label=_("Age High"),
            description=_("The max age in the participants."),
            size=10,
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    IntegerField('AgeLow',
        widget=IntegerWidget(
            label=_("Age low"),
            description=_("The min age in the participants."),
            size=10,
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    IntegerField('NumParticipants',
        widget=IntegerWidget(
            label=_("Number Participants"),
            description=_("The number of participants in this study."),
            size=10,
            visible={'edit': 'visible', 'view': 'visible'},
        )),
    # ReferenceField('Biospecimen',
    #     required=1,
    #     multiValued=1,
    #     vocabulary_display_path_bound=sys.maxint,
    #     vocabulary='_getBiospecimensDisplayList',
    #     allowed_types=('BioSpecimen',),
    #     relationship='BioSpecimenProject',
    #     referenceClass=HoldingReference,
    #     widget=MultiSelectionWidget(
    #        label=_("Biospecimen Type"),
    #        description=_("Select one or more of Biospecimen types. " + \
    #                      "The kit assembly process depends on the types " + \
    #                      "selected here."),
    #     )),

    LinesField('Biospecimens',
        vocabulary='_getBiospecimensDisplayList',
        widget=MultiSelectionWidget(
           modes=('edit',),
           label=_("Biospecimens"),
           description=_(
               "Multi-widget. Use to select more than one biospecimens. Selecting a biospecimen import "
               "the analyses related."),
           visible={'edit': 'visible', 'view': 'visible'},
        )),

    LinesField('Analyses',
        vocabulary='_getBiospecimensDisplayList',
        widget=MultiSelectionWidget(
           modes=('edit',),
           label=_("Analyses"),
           description=_(
               "Multi-widget. Use to select more than one Analyses."),
           visible={'edit': False, 'view': False},
        )),
))
schema['title'].required = True
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}


class Project(BaseContent):
    security = ClassSecurityInfo()
    implements(IProject)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getBiospecimensDisplayList(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title) \
                 for i in bsc(portal_type='BioSpecimen',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        return DisplayList(list(items))

registerType(Project, config.PROJECTNAME)
