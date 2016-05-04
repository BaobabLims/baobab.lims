from Products.Archetypes.public import *
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.references import HoldingReference
from bika.sanbi import bikaMessageFactory as _
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.sanbi.interfaces import IProject
from bika.sanbi import config
import sys

schema = BikaSchema.copy() + Schema((
    ReferenceField('ClientID',
        required=1,
        allowed_types=('Client',),
        relationship='ClientProject',
        vocabulary_display_path_bound=sys.maxsize,
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
           checkbox_bound=0,
           label=_("Client"),
           description=_("Select the project owner."),
           size=50,
           showOn=True,
           visible=True,
        )),

    StringField('StudyType',
        searchable=True,
        widget=StringWidget(
            label=_('Type of study'),
            visible=False,
        )),

    IntegerField('AgeHigh',
        widget=IntegerWidget(
         label=_("Age High"),
         description=_("The max age in the participants."),
         visible=False
        )),

    IntegerField('AgeHigh',
        widget=IntegerWidget(
         label=_("Age low"),
         description=_("The min age in the participants."),
         visible=False
        )),
))
schema['title'].required = True
schema['title'].widget.visible = True
schema['description'].widget.visible = True


class Project(BaseContent):
    security = ClassSecurityInfo()
    implements(IProject)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(Project, config.PROJECTNAME)
