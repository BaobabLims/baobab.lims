from Products.Archetypes.references import HoldingReference
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from Products.Archetypes import public as at
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.interface import implements

from zope.container.contained import ContainerModifiedEvent

from bika.lims.fields import *
from bika.lims.browser.widgets import ReferenceWidget as bikaReferenceWidget
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.workflow import doActionFor
from bika.sanbi import bikaMessageFactory as _
import sys

class AnalysisRequestSchemaExtender(object):
    adapts(IAnalysisRequest)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField(
            'Project',
            vocabulary_display_path_bound=sys.maxsize,
            allowed_types=('Project',),
            referenceClass=HoldingReference,
            relationship='AnalysisRequestProject',
            mode="rw",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=bikaReferenceWidget(
                label=_("Project"),
                description=_("Select the project of the AR."),
                size=20,
                visible={'edit': 'invisible',
                         'view': 'visible',
                         'add': 'edit',
                         'header_table': 'visible',
                         'sample_due': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'invisible'},
                         'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
                         'verified': {'view': 'visible', 'edit': 'invisible'},
                         'published': {'view': 'visible', 'edit': 'invisible'},
                         'invalid': {'view': 'visible', 'edit': 'invisible'},
                         'rejected': {'view': 'visible', 'edit': 'invisible'},
                         },
                catalog_name='bika_catalog',
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields

class AnalysisRequestSchemaModifier(object):
    adapts(IAnalysisRequest)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        return schema

def ObjectModifiedEventHandler(instance, event):
    """update certain field values of the AR created
    """
    if isinstance(event, ContainerModifiedEvent):
        ar_analyses = instance.getAnalyses(full_objects=True)
        sample = instance.getSample()
        partition = sample.objectValues('SamplePartition')[0]
        workflow = getToolByName(sample, 'portal_workflow')
        sample_state = workflow.getInfoFor(sample, 'review_state')
        for analysis in ar_analyses:
            doActionFor(analysis, sample_state)

        for analysis in ar_analyses:
            analysis.setSamplePartition(partition)

