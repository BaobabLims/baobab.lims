from bika.sanbi import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from AccessControl import ClassSecurityInfo
from bika.sanbi.config import PROJECTNAME
from zope.interface import implements
from bika.sanbi.interfaces import ILabAnalysis
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFCore.utils import getToolByName

schema = BikaSchema.copy() + Schema((
    LinesField('Biospecimens',
           vocabulary='_get_biospecimens_displaylist',
           widget=MultiSelectionWidget(
               modes=('edit'),
               label=_("Biospecimens"),
               description=_(
                   "Multi-select widget. Use to select more than one biospecimen."),
               visible=True,
           )),
))

schema['title'].required = True
schema['title'].widget.visible = True
schema['description'].widget.visible = True

class LabAnalysis(BaseContent):
    security = ClassSecurityInfo()
    implements(ILabAnalysis, IConstrainTypes)
    schema = schema

    def _get_biospecimens_displaylist(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title) \
                 for i in bsc(portal_type='BioSpecimen',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        return DisplayList(list(items))

registerType(LabAnalysis, PROJECTNAME)