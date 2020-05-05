from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from zope.interface import implements
from zope.component import adapts
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.public import *

from bika.lims.fields import ExtReferenceField
from bika.lims.interfaces import ISampleType
from bika.lims.browser.widgets.referencewidget import ReferenceWidget as bika_ReferenceWidget

from baobab.lims import bikaMessageFactory as _
from baobab.lims.browser.widgets import ProjectAnalysesWidget


class SampleTypeSchemaExtender(object):
    adapts(ISampleType)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField(
            'Service',
            schemata='Analyses',
            multiValued=1,
            allowed_types=('AnalysisService',),
            relationship='SampleTypeAnalysisService',
            widget=ProjectAnalysesWidget(
               label=_("Sample Analyses"),
               description=_("The analyses included in this sample type, grouped per category."),
            )
        ),
        ExtReferenceField(
            'SampleMatrix',
            required=0,
            allowed_types=('SampleMatrix',),
            vocabulary='SampleMatricesVocabulary',
            relationship='SampleTypeSampleMatrix',
            referenceClass=HoldingReference,
            widget=ReferenceWidget(
                checkbox_bound=0,
                label=_("Sample Matrix"),
                visible=False
            ),
        ),
        ReferenceField(
            'ContainerType',
            required=0,
            allowed_types=('ContainerType',),
            vocabulary='ContainerTypesVocabulary',
            relationship='SampleTypeContainerType',
            widget=ReferenceWidget(
                checkbox_bound=0,
                label=_("Default Container Type"),
                visible=False,
                description=_(
                    "The default container type. New sample partitions "
                    "are automatically assigned a container of this "
                    "type, unless it has been specified in more details "
                    "per analysis service"),
            ),
        ),
        ExtReferenceField(
            'SamplePoints',
            required=0,
            multiValued=1,
            allowed_types=('SamplePoint',),
            vocabulary='SamplePointsVocabulary',
            relationship='SampleTypeSamplePoint',
            widget=bika_ReferenceWidget(
                label=_("Sample Points"),
                visible=False,
                description=_("The list of sample points from which this sample "
                             "type can be collected.  If no sample points are "
                             "selected, then all sample points are available."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        return schematas
