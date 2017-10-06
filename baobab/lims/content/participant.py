from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget
from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IParticipant

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

Sex = StringField(
        'Sex',
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getSexes',
        widget=BikaSelectionWidget(
            description=_("Select the sex of the participant"),
            format='select',
            label=_("Sex"),
            visible={'edit': 'visible', 'view': 'visible'},
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
        widget=BikaSelectionWidget(
            description=_("Whether the age is in years, months, weeks, days etc"),
            format='select',
            label=_("Age Unit"),
            visible={'edit': 'visible', 'view': 'visible'},
        )
    )

schema = BikaSchema.copy() + Schema((
    ParticipantID,
    Sex,
    Age,
    AgeUnit
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
        return ['Female', 'Male', 'Unknown', 'Undifferentiated']

    def getAgeUnits(self):
        return ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes']


registerType(Participant, config.PROJECTNAME)