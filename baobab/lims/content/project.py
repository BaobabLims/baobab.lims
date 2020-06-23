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
from bika.lims.browser.widgets import ReferenceWidget

schema = BikaSchema.copy() + Schema((

    StringField(
        'ProjectType',
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getProjectTypes',
        widget=SelectionWidget(
            label=_("Type of Project"),
            description=_("The type of project this is"),
            visible={'edit': 'visible', 'view': 'visible'},
            render_own_label=True,
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

    StringField(
        'ProjectCode',
        searchable=True,
        widget=StringWidget(
            label=_('Project Code'),
            visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    DateTimeField(
        'StartDate',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=DateTimeWidget(
            label=_("Start Date"),
            visible={'edit': 'visible', 'view': 'visible'},
    )),

    DateTimeField(
        'EndDate',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=DateTimeWidget(
            label=_("End Date"),
            visible={'edit': 'visible', 'view': 'visible'},
    )),

    StringField(
        'ProjectTheme',
        widget=StringWidget(
            label=_("Project Theme"),
            description=_("The theme of this project."),
            visible={'edit': 'visible', 'view': 'visible'},
        )
    ),

    StringField(
        'ProjectAccepted',
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getProjectAcceptedOptions',
        widget=SelectionWidget(
        format='radio',
        label=_("Project Accepted"),
            description=_("Indicates if project is accepted or not"),
            visible={'edit': 'visible', 'view': 'visible'},
            render_own_label=True,
        )
    ),

    TextField(
        'RefuseReason',
        allowable_content_types=('text/plain',),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            label=_("Reason for Refusal"),
            description=_("Reason why this project has been refused.")
        ),
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

    def getProjectAcceptedOptions(self):
        return ['Accepted', 'Rejected']

    def getProjectTypes(self):
        return ['Surveillance', 'Diagnostic', 'Research', 'Routine', 'Project', 'Memory']

registerType(Project, config.PROJECTNAME)
