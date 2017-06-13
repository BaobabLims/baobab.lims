from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from zope.interface import implements
from zope.component import adapts

from bika.lims.fields import ExtReferenceField
from bika.lims.interfaces import ISampleType
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
