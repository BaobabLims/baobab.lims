from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from zope.interface import implements
from zope.component import adapts

from bika.lims.browser.widgets import AnalysisProfileAnalysesWidget
from bika.lims.controlpanel.bika_sampletypes import SampleTypesView
from bika.lims.fields import ExtReferenceField
from bika.lims.interfaces import ISampleType
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.browser.widgets import ProjectAnalysesWidget

class SampleTypeSchemaExtender(object):
    adapts(ISampleType)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField(
            'Service',
            schemata='Analyses',
            required=1,
            multiValued=1,
            allowed_types=('AnalysisService',),
            relationship='SampleTypeAnalysisService',
            widget=ProjectAnalysesWidget(
               label=_("Sample Analyses"),
               description=_("The analyses included in this sample type, grouped per category"),
            )
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        return schematas
