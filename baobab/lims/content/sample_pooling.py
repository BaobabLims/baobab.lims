from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from zope.interface import implements
from Products.CMFCore import permissions

from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget

from baobab.lims.config import PROJECTNAME
from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import ISamplePooling

from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import getToolByName


DateCreation = DateTimeField(
    'DateCreated',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Created"),
        description=_("Define when the sample has been created."),
        show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

PersonPooling = StringField(
    'PersonPooling',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Person Pooling"),
        description=_("The person pooling these samples."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

InputSamples = ReferenceField(
    'InputSamples',
    schemata='Input Samples',
    multiValued=1,
    allowed_types=('InputSample'),
    referenceClass=HoldingReference,
    relationship='PoolingInputSample',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Input Samples"),
        description=_("Select input samples to pool"),
        size=40,
        base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='bika_catalog',
        showOn=True
    )
)

ResultSamples = ReferenceField(
    'ResultSamples',
    schemata='Result Samples',
    multiValued=1,
    allowed_types=('ResultSample'),
    referenceClass=HoldingReference,
    relationship='PoolingResultSample',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Result Samples"),
        description=_("The result samples that result from pooling"),
        size=40,
        base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='bika_catalog',
        showOn=True
    )
)

# InputSamples = StringField(
#     'InputSamples',
#     schemata='Input Samples',
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     widget=StringWidget(
#         label=_("Input Samples"),
#         description=_("Input samples to pool"),
#         size=40,
#         visible={'edit': 'visible', 'view': 'invisible'},
#         showOn=True
#     )
# )

# ResultSamples = StringField(
#     'ResultSamples',
#     schemata='Result Samples',
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     widget=StringWidget(
#         label=_("Result Samples"),
#         description=_("Samples resulting from pooling"),
#         size=40,
#         visible={'edit': 'visible', 'view': 'invisible'},
#         showOn=True
#     )
# )

schema = BikaSchema.copy() + Schema((
    DateCreation,
    PersonPooling,
    InputSamples,
    ResultSamples,
))


schema['title'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].schemata = 'default'


class SamplePooling(BaseContent):
    implements(ISamplePooling)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # def get_input_samples(self):
    #     pc = getToolByName(self, 'portal_catalog')
    #     path = "/".join(self.getPhysicalPath())
    #     brains = pc.searchResults(
    #         portal_type='InputSample',
    #         inactive_state='active',
    #         # sort_on='sortable_title',
    #         path={'query': path, 'level': 0})
    #
    #     samples = []
    #     for brain in brains:
    #         input_sample = brain.getObject()
    #         sample = input_sample.getField('SelectedSample').get(input_sample)
    #         samples.append(sample)
    #
    #     return samples

    # def get_result_samples(self):
    #     pc = getToolByName(self, 'portal_catalog')
    #     path = "/".join(self.getPhysicalPath())
    #     brains = pc.searchResults(
    #         portal_type='ResultSample',
    #         inactive_state='active',
    #         # sort_on='sortable_title',
    #         path={'query': path, 'level': 0})
    #
    #     samples = []
    #     for brain in brains:
    #         input_sample = brain.getObject()
    #         sample = input_sample.getField('SelectedSample').get(input_sample)
    #         samples.append(sample)
    #
    #     return samples

    def get_input_samples(self):
        input_samples = self.getInputSamples()

        samples = []
        for input_sample in input_samples:
            sample = input_sample.getField('SelectedSample').get(input_sample)
            samples.append(sample)

        return samples

    def get_result_samples(self):
        result_samples = self.getResultSamples()

        samples = []
        for result_sample in result_samples:
            sample = result_sample.getField('FinalSample').get(result_sample)
            samples.append(sample)

        return samples


registerType(SamplePooling, PROJECTNAME)