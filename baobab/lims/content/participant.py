from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IParticipant
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.references import HoldingReference
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget

import sys

ParticipantID = StringField(
        'ParticipantID',
        required=1,
        searchable=True,
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Participant ID"),
            description=_("The unique ID code assigned to the participant."),
            visible={'edit': 'visible',
                     'view': 'visible'},
        )
    )

SelectedProject = ReferenceField(
        'SelectedProject',
        #multiValued=1,
        allowed_types=('Project'),
        relationship='ParticipantProjects',
        widget=bika_ReferenceWidget(
            label=_("Select Projects"),
            description=_("Select projects for participant"),
            size=40,
            visible={'edit': 'visible', 'view': 'visible'},
            catalog_name='bika_catalog',
            showOn=True
        )
    )

CaseControl = StringField(
        'CaseControl',
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getCaseControl',
        widget=SelectionWidget(
            format='select',
            label=_("Case or Control Group"),
            description=_("Select whether the participant is in a control group or one of the case participants."),
            visible={'edit': 'visible', 'view': 'visible'},
            render_own_label=True,
        )
    )

FirstName = StringField(
        'FirstName',
        required=0,
        searchable=True,
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("First Name"),
            description=_("The first name of the participant."),
            visible={'edit': 'visible',
                     'view': 'visible'},
        )
    )

LastName = StringField(
        'LastName',
        required=0,
        searchable=True,
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Last Name"),
            description=_("The last name of the participant."),
            visible={'edit': 'visible',
                     'view': 'visible'},
        )
    )

Sex = StringField(
        'Sex',
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getSexes',
        widget=SelectionWidget(
            format='select',
            label=_("Sex"),
            description=_("Select the sex of the participant"),
            visible={'edit': 'visible', 'view': 'visible'},
            render_own_label=True,
        )
    )

Age = FixedPointField(
        'Age',
        required=1,
        default="0.00",
        widget=DecimalWidget(
            label=_("Age"),
            size=15,
            description=_("The age of the participant."),
            visible={'edit': 'visible', 'view': 'visible'}
        )
    )

AgeUnit = StringField(
        'AgeUnit',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getAgeUnits',
        widget=SelectionWidget(
            format='select',
            label=_("Age Unit"),
            description=_("Whether the age is in years, months, weeks, days etc"),
            visible={'edit': 'visible', 'view': 'visible'},
            render_own_label=True,
        )
    )

DiseasesList = ReferenceField(
        'DiseasesList',
        multiValued=1,
        allowed_types=('Disease'),
        relationship='ParticipantDiseases',
        widget=bika_ReferenceWidget(
            label=_("Diseases"),
            description=_("Select diseases that affects participant"),
            size=40,
            visible={'edit': 'visible', 'view': 'visible'},
            catalog_name='bika_catalog',
            showOn=True
        )
    )

schema = BikaSchema.copy() + Schema((
    ParticipantID,
    SelectedProject,
    CaseControl,
    FirstName,
    LastName,
    Sex,
    Age,
    AgeUnit,
    DiseasesList
))
schema['title'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class Participant(BaseContent):
    security = ClassSecurityInfo()
    implements(IParticipant, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getSexes(self):
        return ['Male', 'Female', 'Unknown', 'Undifferentiated']

    def getAgeUnits(self):
        return ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes']

    def getCaseControl(self):
        return ['Case', 'Control']

registerType(Participant, config.PROJECTNAME)