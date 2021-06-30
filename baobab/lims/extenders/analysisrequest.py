from Products.Archetypes.references import HoldingReference
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.container.contained import ContainerModifiedEvent

from bika.lims.fields import *
from bika.lims.browser.widgets import ReferenceWidget as bikaReferenceWidget
from bika.lims.interfaces import IAnalysisRequest
# from bika.lims.interfaces import IAnalysisRequest, ISample
from bika.lims.workflow import doActionFor
from bika.lims.content.analysisrequest import AnalysisRequest as BaseAR

from baobab.lims import bikaMessageFactory as _

import sys


class ExtFixedPointField(ExtensionField, FixedPointField):
    "Field extender"


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
        # ExtReferenceField(
        #     'Sample',
        #     allowed_types=('VirusSample', 'Sample'),
        #     referenceClass=HoldingReference,
        #     relationship='AnalysisRequestSample',
        #     mode="rw",
        #     read_permission=permissions.View,
        #     write_permission=permissions.ModifyPortalContent,
        #     widget=bikaReferenceWidget(
        #         label=_("Sample"),
        #         description=_("Select a sample to create a secondary AR"),
        #         size=20,
        #         render_own_label=True,
        #         visible={
        #             'edit': 'visible',
        #             'view': 'visible',
        #             'add': 'edit',
        #             'header_table': 'visible',
        #             'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
        #             'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
        #             'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
        #             'sampled': {'view': 'visible', 'edit': 'invisible'},
        #             'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
        #             'sample_due': {'view': 'visible', 'edit': 'invisible'},
        #             'sample_prep': {'view': 'visible', 'edit': 'invisible'},
        #             'sample_received': {'view': 'visible', 'edit': 'invisible'},
        #             'attachment_due': {'view': 'visible', 'edit': 'invisible'},
        #             'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
        #             'verified': {'view': 'visible', 'edit': 'invisible'},
        #             'published': {'view': 'visible', 'edit': 'invisible'},
        #             'invalid': {'view': 'visible', 'edit': 'invisible'},
        #             'rejected': {'view': 'visible', 'edit': 'invisible'},
        #         },
        #         showOn=True,
        #         catalog_name='portal_catalog',
        #         base_query={'object_provides': ISample.__identifier__},
        #     ),
        # ),
        ExtFixedPointField(
            'Volume',
            required=1,
            default="0.00",
            widget=DecimalWidget(
                label=_("Volume"),
                size=15,
                description=_("The sample volume needed for the analyses."),
                visible={'edit': 'visible',
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
                render_own_label=True,
            )
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        sch = schematas['default']
        sch.remove('Volume')
        sch.insert(sch.index('Batch'), 'Volume')
        return schematas

    def getFields(self):
        return self.fields

class AnalysisRequestSchemaModifier(object):
    adapts(IAnalysisRequest)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        # schema['Sample'].allowed_types = ('Sample', 'VirusSample')
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


class AnalysisRequest(BaseAR):
    """ Inherits from bika.lims.content.AnalysisRequest
    """
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from baobab.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getClient(self):
        if self.aq_parent.portal_type == 'Client':
            return self.aq_parent
        else:
            return self.aq_parent.getClient()

    def getRequestedAnalyses(self):
        """It returns all requested analyses, even if they belong to an
        analysis profile or not.
        """
        #
        # title=Get requested analyses
        #
        result = []
        workflow = getToolByName(self, 'portal_workflow')
        for analysis in self.getAnalyses(full_objects=True):
            review_state = workflow.getInfoFor(analysis, 'review_state')
            if review_state == 'not_requested':
                continue
            result.append(analysis)
        return result


from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
# Overrides type bika.lims.content.sample
atapi.registerType(AnalysisRequest, PROJECTNAME)
