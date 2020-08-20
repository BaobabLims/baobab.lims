from AccessControl import ClassSecurityInfo
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.public import (
    BaseContent, BooleanField, Schema, StringField, StringWidget,
    ReferenceField, registerType)
from Products.Archetypes.Widget import SelectionWidget
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IMaldiTof

from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.utils import getUsers


BioBankNumber = StringField(
    'BioBankNumber',
    required=1,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Biobank number"),
        description=_("MALDI-TOF Biobank number."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)
DateOfMaldiTof = DateTimeField(
    'DateOfMaldiTof',
    required=0,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date of MaldiTof"),
        description=_("Date of Maldi-TOF."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)
Strain = ReferenceField(
    'Strain',
    allowed_types=('Strain',),
    relationship='MaldiTofStrain',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_('Strain reported'),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_('Select the Strain for the Collection Request.'),
    )
)
Result = ReferenceField(
    'Result',
    allowed_types=('Strain',),
    relationship='MaldiTofStrain',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_('MALDI-TOF result'),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_('Select the Strain for the Collection Request.'),
    )
)
LevelOfConfidence = StringField(
    'LevelOfConfidence',
    required=1,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Level of confidence"),
        description=_("Level of confidence."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)
Score = StringField(
    'Score',
    required=1,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Score"),
        description=_("Score"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)
Analyst = StringField(
    'Analyst',
    required=1,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getAnalysts',
    acquire=True,
    widget=SelectionWidget(
        format="select",
        label=_("Analyst"),
        description=_(""),
    ),
    )
Conformity = BooleanField(
        'Conformity',
        required=1,
        format="select",
        widget=SelectionWidget(
            label=_("Conformity"),
            description=_(''),
            visible={'view': 'visible', 'edit': 'visible'},
        )
    )
NonConformity = ReferenceField(
    'NonConformity',
    allowed_types=('Conformity',),
    relationship='MaldiTofNonConformity',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_('Non-conformity'),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=False,
        size=30,
        showOn=True,
        description=_('Select the Non-Conformity.'),
        catalog_name='portal_catalog',
        colModel=[
            {'columnName': 'Title',
             'width': '30',
             'label': _('Title'),
             'align': 'left'},
            {'columnName': 'NonConformityAction',
             'width': '70',
             'label': _('NonConformityAction'),
             'align': 'left'},
            # UID is required in colModel
            {'columnName': 'UID', 'hidden': True},
        ],
    )
)

schema = BikaSchema.copy() + Schema((
    BioBankNumber,
    DateOfMaldiTof,
    Strain,
    Result,
    LevelOfConfidence,
    Score,
    Analyst,
    Conformity,
    NonConformity,

))

schema['title'].required = False
schema['title'].widget.visible = False


class MaldiTof(BaseContent):
    security = ClassSecurityInfo()
    implements(IMaldiTof, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getAnalysts(self):
        analysts = getUsers(self, ['Manager', 'LabManager', 'Analyst'])
        analysts = analysts.sortedByKey()
        return analysts

    def getAnalystName(self):
        """ Returns the name of the currently assigned analyst
        """
        mtool = getToolByName(self, 'portal_membership')
        analyst = self.getAnalyst().strip()
        analyst_member = mtool.getMemberById(analyst)
        if analyst_member is not None:
            return analyst_member.getProperty('fullname')
        else:
            return ''


registerType(MaldiTof, config.PROJECTNAME)
