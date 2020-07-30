from baobab.lims.idserver import renameAfterCreation
from baobab.lims.utils.send_email import send_email
from bika.lims.browser import BrowserView

from Products.CMFCore.utils import getToolByName
import json

class AjaxApproveCollectionRequest(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):

        super(AjaxApproveCollectionRequest, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.workflow = getToolByName(self.context, 'portal_workflow')
        self.collection_request = []
        self.errors = []

    def __call__(self):

        try:
            if 'approval_data' not in self.request.form:
                raise Exception('No valid collection request approval data has been send')

            approval_data = json.loads(self.request.form['approval_data'])
            collection_request_details = approval_data.get('approval_data_details', None)
            collection_request_human_samples = approval_data.get('approval_data_human_rows', None)
            collection_request_microbe_samples = approval_data.get('approval_data_microbe_rows', None)

            # raise Exception('This is the exception')
            self.confirm_collection_request_status(collection_request_details['collection_request_uid'])

            # process input and result samples
            human_collection_requests = self.approve_collection_request_human_samples(
                collection_request_human_samples,
            )
            microbe__collection_requests = self.approve_collection_request_microbe_samples(
                collection_request_microbe_samples,
            )
            collection_request_obj = self.approve_collection_request_object(collection_request_details)


            for obj in human_collection_requests:
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)

            for obj in microbe__collection_requests:
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)

        except Exception as e:
            error_message = json.dumps({'error_message': str(e)})
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(500)
            self.request.RESPONSE.write(error_message)
        else:
            output = json.dumps({
                'url': collection_request_obj.absolute_url()
            })

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(200)
            self.request.RESPONSE.write(output)

    def get_client_email_address(self, collection_request):
        try:
            client = collection_request.getField('Client').get(collection_request)
            return client.getField('EmailAddress').get(client)
        except:
            return ''

    def get_approved_email_message(self, collection_request):
        message = '''
        Dear Client

        We are pleased to inform you that your request for collection %s has been accepted. 
        Please contact the IPCI for the deposit of your samples. 
        Drop off days are Mondays and Wednesdays from 8 a.m. to 11:30.  

        Best regards.
        From the Secretariat of BeReB IPCI
        ''' % collection_request.getField('RequestNumber').get(collection_request)

        return message

    def get_rejected_email_message(self, collection_request):
        message = '''
        Dear Client

        Unfortunately, we cannot follow up on your request for the following reasons: 
        %s 
        
        Please contact us for more information. 
                
        Best regards.
        From the Secretariat of BeReB IPCI
        ''' % collection_request.getField('ReasonForEvaluation').get(collection_request)

        return message

    def confirm_collection_request_status(self, collection_request_uid):
        obj = self.get_content_type(collection_request_uid)
        review_state = self.workflow.getInfoFor(obj, 'review_state')

        print('-------review state')
        print(review_state)

        if review_state == 'finalised':
            raise Exception('This collection request is already finalised and cannot be changed anymore.')

    def approve_collection_request_object(self, collection_request_details):

        obj = self.get_content_type(collection_request_details['collection_request_uid'])

        obj.edit(
            DateEvaluated=collection_request_details['date_evaluated'],
            ResultOfEvaluation=collection_request_details['result_of_evaluation'],
            ReasonForEvaluation=collection_request_details['reason_for_evaluation'],
        )

        if collection_request_details['result_of_evaluation'] in ['Approved', 'Conditionally Approved', 'Rejected']:
            self.workflow.doActionFor(obj, 'make_ready')
            self.workflow.doActionFor(obj, 'finalise')

            self.email_confirmation_result(obj)

        obj.reindexObject()
        return obj

    def email_confirmation_result(self, collection_request):
        receiver = self.get_client_email_address(collection_request)

        if collection_request.getField('ResultOfEvaluation').get(collection_request) in ['Approved', 'Conditionally Approved']:
            message = self.get_approved_email_message(collection_request)
            subject = 'Approval of collection request %s' % collection_request.getField('RequestNumber').get(collection_request)

        if collection_request.getField('ResultOfEvaluation').get(collection_request) in ['Rejected']:
            message = self.get_rejected_email_message(collection_request)
            subject = 'Rejection of collection request %s' % collection_request.getField('RequestNumber').get(collection_request)

        send_email(self.context, receiver, receiver, subject, message)

    def approve_collection_request_human_samples(self, collection_request_human_rows):

        human_collection_requests = []

        for row_data in collection_request_human_rows:
            human_collection_request = self.get_content_type(row_data['uid'])
            print('---------Inside the human collection request')
            if row_data['approval'] in ['', 'approved', 'rejected']:
                print('------approved')
                human_collection_request.getField('Approved').set(human_collection_request, row_data['approval'])
                human_collection_requests.append(human_collection_request)

        return human_collection_requests

    def approve_collection_request_microbe_samples(self, collection_request_microbe_rows):

        microbe_collection_requests = []

        for row_data in collection_request_microbe_rows:
            microbe_collection_request = self.get_content_type(row_data['uid'])
            if row_data['approval'] in ['', 'approved', 'rejected']:
                microbe_collection_request.getField('Approved').set(microbe_collection_request, row_data['approval'])
                microbe_collection_requests.append(microbe_collection_request)

        return microbe_collection_requests



    #
    #
    # def create_collection_request_microbe_samples(self, collection_request_microbe_rows):
    #
    #     collection_request_microbe_samples = []
    #
    #     for row_data in collection_request_microbe_rows:
    #         collection_request_microbe_sample = self.create_microbe_sample_request(row_data)
    #         collection_request_microbe_samples.append(collection_request_microbe_sample)
    #
    #     return collection_request_microbe_samples
    #
    # def create_human_sample_request(self, collection_request_microbe_sample):
    #
    #     try:
    #         human_sample_requests = self.context.human_sample_requests
    #         sample_type = self.get_content_type(collection_request_microbe_sample.get('sample_type', 'unknown'))
    #         obj = _createObjectByType('HumanSampleRequest', human_sample_requests, tmpID())
    #
    #         obj.edit(
    #             Barcode=collection_request_microbe_sample['barcode'],
    #             SampleType=sample_type,
    #             Volume=collection_request_microbe_sample['volume'],
    #             Unit=collection_request_microbe_sample['unit'],
    #         )
    #
    #         obj.unmarkCreationFlag()
    #         renameAfterCreation(obj)
    #
    #         return obj
    #
    #     except Exception as e:
    #         print('---------create human sample request error')
    #         print(str(e))
    #         return None
    #
    # def create_microbe_sample_request(self, collection_request_microbe_sample):
    #
    #     try:
    #         microbe_sample_requests = self.context.microbe_sample_requests
    #         strain = self.get_content_type(collection_request_microbe_sample.get('strain', 'unknown'))
    #         sample_type = self.get_content_type(collection_request_microbe_sample.get('sample_type', 'unknown'))
    #         obj = _createObjectByType('MicrobeSampleRequest', microbe_sample_requests, tmpID())
    #
    #         obj.edit(
    #             Identification=collection_request_microbe_sample['identification'],
    #             Strain=strain,
    #             Origin=collection_request_microbe_sample['origin'],
    #             SampleType=sample_type,
    #             Phenotype=collection_request_microbe_sample['phenotype'],
    #         )
    #
    #         obj.unmarkCreationFlag()
    #         renameAfterCreation(obj)
    #
    #         return obj
    #
    #     except Exception as e:
    #         print('---------create microbe sample request error')
    #         print(str(e))
    #         return None

    def get_sample(self, sample_uid):
        try:
            brains = self.pc(UID=sample_uid)
            return brains[0].getObject()
        except Exception as e:
            raise Exception('Sample to be pooled not found')

    def get_project(self, sample_uid):
        try:
            selected_sample = self.get_content_type(sample_uid)
            return selected_sample.aq_parent
        except Exception as e:
            raise Exception('No suitable sample has been selected')

    def get_sample_type(self, sample_type_uid):
        try:
            brains = self.pc(UID=sample_type_uid)
            return brains[0].getObject()
        except Exception as e:
            return None

    def get_content_type(self, content_type_uid, catalog="portal_catalog"):
        try:
            catalog = self.get_catalog(catalog)
            brains = catalog(UID=content_type_uid)
            return brains[0].getObject()
        except Exception as e:
            return None

    def get_catalog(self, catalog="portal_catalog"):
        if catalog == 'bika_setup_catalog':
            return getToolByName(self.context, 'bika_setup_catalog')

        if catalog == 'portal_catalog':
            return getToolByName(self.context, 'portal_catalog')
