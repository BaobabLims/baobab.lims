# from DateTime import DateTime
from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView
from baobab.lims.utils.audit_logger import AuditLogger
# from baobab.lims.utils.local_server_time import getLocalServerTime

import json


class CollectionRequestView(BrowserView):
    template = ViewPageTemplateFile('templates/collectionrequest_view.pt')

    def __init__(self, context, request):
        super(CollectionRequestView, self).__init__(context, request)
        self.title = self.context.Title()
        self.context = context
        self.request = request

    def __call__(self):

        workflow = getToolByName(self.context, 'portal_workflow')
        reviewState = workflow.getInfoFor(self.context, 'review_state')

        self.reviewState = reviewState
        self.absolute_url = self.context.absolute_url()
        self.id = self.context.getId()
        self.collection_request_uid = self.context.UID()

        self.client = self.get_client(self.context)
        self.request_number = self.context.getRequestNumber()
        self.date_of_request = self.context.getDateOfRequest()
        self.collect_microbe_samples = self.context.getCollectMicrobeSamples()
        self.collect_human_samples = self.context.getCollectHumanSamples()
        # self.number_requested = self.context.getNumberRequested()
        self.date_evaluated= self.context.getDateEvaluated()
        self.result_of_evaluation= self.context.getResultOfEvaluation()
        self.reason_for_evaluation= self.context.getReasonForEvaluation()

        self.human_sample_request_rows = self.prepare_human_sample_request_rows()
        self.microbe_sample_request_rows = self.prepare_microbe_sample_request_rows()

        self.microbe_sample_requests = len(self.microbe_sample_request_rows) > 0
        self.human_sample_requests = len(self.human_sample_request_rows) > 0
        #
        # print('--------microbe  %s' % (self.microbe_sample_request_rows))
        # print('--------human  %s' % (self.human_sample_request_rows))

        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

    def prepare_human_sample_request_rows(self):

        human_sample_request_rows = self.context.get_human_sample_requests()
        prepared_request_rows = []

        for sample_request in human_sample_request_rows:

            prepared_request = {
                'approved': sample_request.getField('Approved').get(sample_request) or '',
                'barcode': sample_request.getField('Barcode').get(sample_request),
                'sample_type': self.get_sample_type(sample_request),
                'sample_package': self.get_sample_package(sample_request),
                'volume': sample_request.getField('Volume').get(sample_request),
                'unit': sample_request.getField('Unit').get(sample_request),
            }
            prepared_request_rows.append(prepared_request)

        return prepared_request_rows

    def prepare_microbe_sample_request_rows(self):

        microbe_sample_request_rows = self.context.get_microbe_sample_requests()
        prepared_request_rows = []

        for sample_request in microbe_sample_request_rows:

            prepared_request = {
                'approved': sample_request.getField('Approved').get(sample_request) or '',
                'identification': sample_request.getField('Identification').get(sample_request),
                'strain': self.get_strain(sample_request),
                'origin': sample_request.getField('Origin').get(sample_request),
                'sample_type': self.get_sample_type(sample_request),
                'phenotype': sample_request.getField('Phenotype').get(sample_request),
            }
            prepared_request_rows.append(prepared_request)

        return prepared_request_rows

    def get_client(self, collection_request):
        try:
            client = collection_request.getField('Client').get(collection_request)
            return client.Title()
        except:
            return ''

    def get_sample_kingdom(self, collection_request):
        try:
            sample_kingdom = collection_request.getSampleKingdom()
            return sample_kingdom.Title()
        except:
            return ''


    def get_sample_type(self, sample_request):
        try:
            sample_type = sample_request.getSampleType()
            return sample_type.Title()
        except:
            return ''

    def get_sample_package(self, sample_request):
        try:
            sample_package = sample_request.getField('SamplePackage').get(sample_request)
            return sample_package.Title()
        except:
            return ''

    def get_strain(self, sample_request):
        try:
            strain = sample_request.getField('Strain').get(sample_request)
            return strain.Title()
        except:
            return ''

class CollectionRequestEdit(BrowserView):
    template = ViewPageTemplateFile('templates/collectionrequest_edit.pt')

    def __call__(self):
        request = self.request
        context = self.context

        if 'submitted' in request:

            context.setConstrainTypesMode(constraintypes.DISABLED)

            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)

            self.perform_collectionrequest_audit(context, request)
            context.getField('description').set(context, self.request.form['description'])
            context.getField('DateCreated').set(context, self.request.form['DateCreated'])
            context.getField('Technician').set(context, self.request.form['Technician'])
            context.getField('Technique').set(context, self.request.form['Technique'])
            context.reindexObject()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return

        return self.template()

    def perform_collectionrequest_audit(self, collectionrequest, request):
        audit_logger = AuditLogger(self.context, 'Centrifugation')
        pc = getToolByName(self.context, "portal_catalog")

        # Description
        if collectionrequest.getField('description').get(collectionrequest) != request.form['description']:
            audit_logger.perform_simple_audit(collectionrequest, 'description', collectionrequest.getField('description').get(collectionrequest),
                                              request.form['description'])

        # Date Created
        date_created = request.form['DateCreated']
        # if date_created:
        #     date_created = DateTime(getLocalServerTime(date_created))
        object_date_created = collectionrequest.getField('DateCreated').get(collectionrequest)
        if not object_date_created:
            object_date_created = ''
        if object_date_created != date_created:
            audit_logger.perform_simple_audit(collectionrequest, 'DateCreated',
                                              object_date_created, date_created)

        # Technician
        audit_logger.perform_reference_audit(collectionrequest, 'Technician',
                                             collectionrequest.getField('Technician').get(collectionrequest),
                                             pc, request.form['Technician_uid'])

        # Technique
        if collectionrequest.getField('Technique').get(collectionrequest) != request.form['Technique']:
            audit_logger.perform_simple_audit(collectionrequest, 'Technique',
                                              collectionrequest.getField('Technique').get(collectionrequest),
                                              request.form['Technique'])

    def prepare_human_sample_request_rows(self):

        human_sample_request_rows = self.context.get_human_sample_requests()
        prepared_request_rows = []

        for sample_request in human_sample_request_rows:
            approved = sample_request.getField('Approved').get(sample_request)
            approval_status = self.get_approval_status(approved)

            prepared_request = {
                'UID': sample_request.UID(),
                'status_approved': approval_status['approved_status'],
                'status_rejected': approval_status['rejected_status'],
                'status_unspecified': approval_status['unspecified_status'],
                'barcode': sample_request.getField('Barcode').get(sample_request),
                'sample_type': self.get_sample_type(sample_request),
                'sample_package': self.get_sample_package(sample_request),
                'volume': sample_request.getField('Volume').get(sample_request),
                'unit': sample_request.getField('Unit').get(sample_request),
            }
            prepared_request_rows.append(prepared_request)

        return prepared_request_rows

    def prepare_microbe_sample_request_rows(self):

        microbe_sample_request_rows = self.context.get_microbe_sample_requests()
        prepared_request_rows = []

        for sample_request in microbe_sample_request_rows:
            approved = sample_request.getField('Approved').get(sample_request)
            approval_status = self.get_approval_status(approved)

            prepared_request = {
                'UID': sample_request.UID(),
                'status_approved': approval_status['approved_status'],
                'status_rejected': approval_status['rejected_status'],
                'status_unspecified': approval_status['unspecified_status'],
                'identification': sample_request.getField('Identification').get(sample_request),
                'strain': self.get_strain(sample_request),
                'origin': sample_request.getField('Origin').get(sample_request),
                'sample_type': self.get_sample_type(sample_request),
                'phenotype': sample_request.getField('Phenotype').get(sample_request),
            }
            prepared_request_rows.append(prepared_request)

        return prepared_request_rows

    def get_approval_status(self, approval):
        approval_status = {
            'rejected_status': False,
            'approved_status': False,
            'unspecified_status': False,
        }

        if approval == 'rejected':
            approval_status['rejected_status'] = True
            return approval_status

        if approval == 'approved':
            approval_status['approved_status'] = True
            return approval_status

        approval_status['unspecified_status'] = True
        return approval_status

    def get_client(self, collection_request):
        try:
            client = collection_request.getField('Client').get(collection_request)
            return client.Title()
        except:
            return ''

    def get_sample_kingdom(self, collection_request):
        try:
            sample_kingdom = collection_request.getSampleKingdom()
            return sample_kingdom.Title()
        except:
            return ''


    def get_sample_type(self, sample_request):
        try:
            sample_type = sample_request.getSampleType()
            return sample_type.Title()
        except:
            return ''

    def get_strain(self, sample_request):
        try:
            strain = sample_request.getField('Strain').get(sample_request)
            return strain.Title()
        except:
            return ''

    def get_sample_package(self, sample_request):
        try:
            sample_package = sample_request.getField('SamplePackage').get(sample_request)
            return sample_package.Title()
        except:
            return ''

    def get_fields_with_visibility(self, visibility, schemata, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():

            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:

                if field.schemata == schemata:
                    fields.append(field)

        return fields

# class GetCentrifugationData(BrowserView):
#
#     def __init__(self, context, request):
#
#         super(GetCentrifugationData, self).__init__(context, request)
#         self.context = context
#         self.request = request
#
#     def __call__(self):
#
#         uc = getToolByName(self.context, 'portal_catalog')
#
#         try:
#             uid = self.request['UID']
#             brains = uc.searchResults(portal_type='Centrifugation', UID=uid)
#             sample_pooling = brains[0].getObject()
#
#             return_val = {
#                 'date_created': str(sample_pooling.getField('DateCreated').get(sample_pooling) or ''),
#             }
#
#             return json.dumps(return_val)
#
#         except:
#             return json.dumps({
#                 'date_created': '',
#             })


class ajaxGetProjects(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetProjects, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        # plone.protect.CheckAuthenticator(self.request)

        rows = []

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="Project")

        for project in brains:
            rows.append({
                project.UID: project.Title
            })

        return json.dumps(rows)


class ajaxGetSampleTypes(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetSampleTypes, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        # plone.protect.CheckAuthenticator(self.request)
        rows = []

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="SampleType")

        for sample_type in brains:
            rows.append({
                sample_type.UID: sample_type.Title
            })

        return json.dumps(rows)
