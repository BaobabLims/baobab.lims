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
from bika.sanbi.browser.widgets import ProjectAnalysesWidget

schema = BikaSchema.copy() + Schema((
    ReferenceField('Client',
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
            description=_("Maximum age of the participants."),
            size=10,
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    IntegerField('AgeLow',
        widget=IntegerWidget(
            label=_("Age low"),
            description=_("Minimum age of the participants."),
            size=10,
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    IntegerField('NumParticipants',
        widget=IntegerWidget(
            label=_("Number of Participants"),
            description=_("Number of participants in the study."),
            size=10,
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    LinesField('Biospectypes',
        vocabulary='_getBiospecimensDisplayList',
        widget=MultiSelectionWidget(
           modes=('edit',),
           label=_("Biospecimen types"),
           description=_(
               "Multi-select widget. Use to select more than one biospecimen type. Selecting a biospecimen type import "
               "the corresponding analysis services."),
           visible={'edit': 'visible', 'view': 'visible'},
        )),

    LinesField('Analyses',
        vocabulary='_getBiospecimensDisplayList',
        widget=MultiSelectionWidget(
           modes=('edit',),
           label=_("Analyses"),
           description=_(
               "Multi-select widget. Select manually or use biospecimen-type widget to select Analysis services. "
               "The services chosen here will be use in Analysis requests."),
           visible={'edit': False, 'view': False},
        )),

    ReferenceField('Service',
           required=1,
           multiValued=1,
           allowed_types=('AnalysisService',),
           relationship='BiospecimenAnalysisService',
           widget=ProjectAnalysesWidget(
               label=_("Analyse Services"),
               description=_(
                   "Multi-checkboxes table. Select manually or use biospecimen-type widget to select Analysis services. "
                   "The services chosen here will be used in Analysis requests."),
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
                 for i in bsc(portal_type='BiospecType',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        return DisplayList(list(items))

registerType(Project, config.PROJECTNAME)
