from Products.Archetypes.public import *
from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from Products.CMFPlone.interfaces import IConstrainTypes

from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.fields import DateTimeField
from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import IProject
from baobab.lims import config
from baobab.lims.browser.widgets import ProjectAnalysesWidget

schema = BikaSchema.copy() + Schema((

    StringField(
        'StudyType',
        searchable=True,
        widget=StringWidget(
            label=_('Type of study'),
            visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    StringField(
        'EthicsFormLink',
        searchable=True,
        widget=StringWidget(
            label=_('Link to Ethics Form'),
            visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    IntegerField(
        'AgeHigh',
        widget=IntegerWidget(
            label=_("Age High"),
            description=_("Maximum age of the participants."),
            size=10,
            visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    IntegerField(
        'AgeLow',
        widget=IntegerWidget(
            label=_("Age low"),
            description=_("Minimum age of the participants."),
            size=10,
            visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    IntegerField(
        'NumParticipants',
        widget=IntegerWidget(
            label=_("Number of Participants"),
            description=_("Number of participants in the study."),
            size=10,
            visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    LinesField(
        'SampleType',
        vocabulary='_getBiospecimensDisplayList',
        widget=MultiSelectionWidget(
            modes=('edit',),
            label=_("Biospecimen Type"),
            description=_(
                "Multi-select widget. Use to select more than one biospecimen type. Selecting a biospecimen type import "
                "the corresponding analysis services."),
            visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    ReferenceField(
        'Service',
        required=0,
        multiValued=1,
        allowed_types=('AnalysisService',),
        relationship='BiospecimenAnalysisService',
        widget=ProjectAnalysesWidget(
           label=_("Analyses"),
           description="",
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
    )),
))

schema['title'].required = True
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['title'].widget.size = 100
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}


class Project(BaseFolder):

    implements(IProject, IConstrainTypes)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getBiospecimensDisplayList(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title) \
                 for i in bsc(portal_type='SampleType',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        return DisplayList(list(items))

    def getClient(self):
        return self.aq_parent if self.aq_parent.portal_type == 'Client' \
                              else ''

    def getClientID(self):
        return self.aq_parent.getId() if self.aq_parent.portal_type == 'Client' \
                                      else ''

registerType(Project, config.PROJECTNAME)
