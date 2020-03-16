from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from zope.interface import implements
# from Products.CMFCore import permissions

from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.Archetypes.references import HoldingReference

from baobab.lims.config import PROJECTNAME
from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import IResultSample

FinalSample = ReferenceField(
    'FinalSample',
    allowed_types=('Sample'),
    referenceClass=HoldingReference,
    relationship='ResultSampleSample',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Result Sample"),
        description=_("The final sample resulting from the pooling"),
        size=40,
        base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='bika_catalog',
        showOn=True
    )
)

FinalVolume = StringField(
    'FinalVolume',
    widget=StringWidget(
        label=_('Final Volume'),
        description=_('The final volume after all selected samples have been pooled.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

FinalVolumeUnit = StringField(
    'FinalVolumeUnit',
    widget=StringWidget(
        label=_('Input Volume Unit'),
        description=_('The unit of the final volume.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)


schema = BikaSchema.copy() + Schema((
    FinalSample,
    FinalVolume,
    FinalVolumeUnit,
))

schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class ResultSample(BaseContent):
    implements(IResultSample)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from baobab.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(ResultSample, PROJECTNAME)

