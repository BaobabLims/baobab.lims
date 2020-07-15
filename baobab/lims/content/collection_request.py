from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.fields import DateTimeField

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import ICollectionRequest
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFPlone.utils import safe_unicode

Client = ReferenceField(
    'Client',
    schemata='Client Information',
    allowed_types=('Client',),
    relationship='CollectionRequestClient',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Client"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Client."),
    )
)

RequestNumber= StringField(
    'RequestNumber',
    schemata='Client Information',
    required=1,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Request Number"),
        description=_("The request Number for this collection request."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

DateOfRequest = DateTimeField(
    'DateOfRequest',
    schemata='Client Information',
    required=0,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date of Request"),
        description=_("The Date this collection request were made."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

SampleKingdom = ReferenceField(
    'SampleKingdom',
    schemata='Client Information',
    allowed_types=('SampleKingdom',),
    relationship='CollectionRequestSampleKingdom',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Sample Kingdom"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Sample Kingdom."),
    )
)

# Identificationz = StringField(
#         'Identificationz',
#         schemata='Client Information',
#         required=0,
#         searchable=True,
#         read_permission=permissions.View,
#         write_permission=permissions.ModifyPortalContent,
#         widget=StringWidget(
#             label=_("Identification"),
#             description=_("The identification of this collection request."),
#             visible={'edit': 'visible', 'view': 'visible'},
#         )
#     )
#
# Strain = ReferenceField(
#     'Strain',
#     schemata='Client Information',
#     allowed_types=('Strain',),
#     relationship='CollectionRequestStrain',
#     referenceClass=HoldingReference,
#     widget=bika_ReferenceWidget(
#         label=_("Select Strain"),
#         visible={'edit': 'visible', 'view': 'visible'},
#         size=30,
#         showOn=True,
#         description=_("Select the Strain."),
#     )
# )
#
# OriginIsolatedFrom = StringField(
#         'OriginIsolatedFrom',
#         schemata='Client Information',
#         read_permission=permissions.View,
#         write_permission=permissions.ModifyPortalContent,
#         vocabulary='getOriginIsolatedFrom',
#         widget=SelectionWidget(
#         label=_("Origin Isolated From"),
#             description=_("The origin this sample has been isolated from."),
#             visible={'edit': 'visible', 'view': 'visible'},
#             render_own_label=True,
#         )
#     )
#
# Phenotype = StringField(
#     'Phenotype',
#     schemata='Client Information',
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     vocabulary='getPhenotype',
#     widget=SelectionWidget(
#         format='select',
#         label=_("Phenotype"),
#         description=_("The Phenotype of this sample."),
#         visible={'edit': 'visible', 'view': 'visible'},
#         render_own_label=True,
#     )
# )

NumberRequested = StringField(
    'NumberRequested',
    schemata='Client Information',
    required=0,
    searchable=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Number Requested"),
        description=_("The number of samples requested for this collection request."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

# ------------------
HumanSampleRequests = ReferenceField(
    'HumanSampleRequests',
    schemata='Sample Requests',
    multiValued=1,
    allowed_types=('HumanSampleRequest'),
    referenceClass=HoldingReference,
    relationship='CollectionRequestHumanSampleRequest',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Human Sample Request"),
        description=_("Select human sample request"),
        size=40,
        # base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='portal_catalog',
        showOn=True
    )
)

MicrobeSampleRequests = ReferenceField(
    'MicrobeSampleRequests',
    schemata='Sample Requests',
    multiValued=1,
    allowed_types=('MicrobeSampleRequest'),
    referenceClass=HoldingReference,
    relationship='CollectionRequestMicrobeSampleRequest',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Microbe Sample Request"),
        description=_("Select microbe sample request"),
        size=40,
        # base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='portal_catalog',
        showOn=True
    )
)

# ------------------
DateEvaluated = DateTimeField(
    'DateEvaluated',
    schemata='Evaluation',
    required=0,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Evaluated"),
        description=_("The date this collection request were evaluated for approval or refusal."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

ResultOfEvaluation = StringField(
        'ResultOfEvaluation',
        schemata='Evaluation',
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getProjectAcceptedOptions',
        widget=SelectionWidget(
        format='select',
        label=_("Result Of Evaluation"),
            description=_("Indicates if collection request has been approved"),
            visible={'edit': 'visible', 'view': 'visible'},
            render_own_label=True,
        )
    )

ReasonForEvaluation = StringField(
        'ReasonForEvaluation',
        schemata='Evaluation',
        allowable_content_types=('text/plain',),
        default_output_type="text/plain",
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=TextAreaWidget(
            label=_("Reason For Evaluation"),
            description=_("Reason for this particular evaluation.")
        ),
    )

schema = BikaSchema.copy() + Schema((
    Client,
    RequestNumber,
    DateOfRequest,
    SampleKingdom,
    # Identificationz,
    # Strain,
    # OriginIsolatedFrom,
    # Phenotype,
    NumberRequested,
    MicrobeSampleRequests,
    HumanSampleRequests,
    DateEvaluated,
    ResultOfEvaluation,
    ReasonForEvaluation,
))
schema['title'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class CollectionRequest(BaseContent):
    security = ClassSecurityInfo()
    implements(ICollectionRequest, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getProjectAcceptedOptions(self):
        return ['Approved', 'Conditionally Approved', 'Rejected']

    def getOriginIsolatedFrom(self):
        return ['Human', 'Animal', 'Plant', 'Environmental']

    def getPhenotype(self):
        return ['Unknown', 'WildType', 'Recombinant']

    def get_human_sample_requests(self):
        # human_sample_requests = self.getHumanSampleRequests()
        human_sample_requests = self.getField('HumanSampleRequests').get(self)
        print('----------Human sample requests')
        print(human_sample_requests)

        requests = []
        for request in human_sample_requests:
            requests.append(request)

        return requests

    def get_microbe_sample_requests(self):
        # microbe_sample_requests = self.getMicrobeSampleRequests()
        microbe_sample_requests = self.getField('MicrobeSampleRequests').get(self)
        print(microbe_sample_requests)

        requests = []
        for request in microbe_sample_requests:
            requests.append(request)

        return requests
        # return []

    # def Title(self):
    #     return safe_unicode(self.getField('SampleDonorID').get(self)).encode('utf-8')
    #
    # def Description(self):
    #     return "Gender %s : Age %s %s" % (self.getSex(), self.getAge(), self.getAgeUnit())
    #
    # def getSexes(self):
    #     return ['Male', 'Female', 'Unknown', 'Undifferentiated']
    #
    # def getAgeUnits(self):
    #     return ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes']

registerType(CollectionRequest, config.PROJECTNAME)