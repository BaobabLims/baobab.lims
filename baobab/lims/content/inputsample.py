from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from zope.interface import implements
# from Products.CMFCore import permissions

from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.Archetypes.references import HoldingReference

from baobab.lims.config import PROJECTNAME
from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import IInputSample

SelectedSample = ReferenceField(
    'SelectedSample',
    allowed_types=('Sample'),
    referenceClass=HoldingReference,
    relationship='InputSampleSample',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Input sample"),
        description=_("One of the selected input samples"),
        size=40,
        base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='bika_catalog',
        showOn=True
    )
)

InputVolume = StringField(
    'InputVolume',
    widget=StringWidget(
        label=_('Input Volume'),
        description=_('The amount of volume that was taken from this sample.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

InputVolumeUnit = StringField(
    'InputVolumeUnit',
    widget=StringWidget(
        label=_('Input Volume Unit'),
        description=_('The unit of the taken volume.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)


schema = BikaSchema.copy() + Schema((
    SelectedSample,
    InputVolume,
    InputVolumeUnit,
))

schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class InputSample(BaseContent):
    implements(IInputSample)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from baobab.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

# def ObjectModifiedEventHandler(instance, event):
#     """ Called if the object is modified.
#         Note from QC 2018-11-05:  As far as I can see this change happens after the object is modified.
#         I tested by altering the Serum Colour and by the time it does a data dump here the object
#         already has the new colour.
#     """
#
#     if instance.portal_type == 'SampleBatch':
#         from baobab.lims.idserver import renameAfterEdit
#         renameAfterEdit(instance)

registerType(InputSample, PROJECTNAME)

