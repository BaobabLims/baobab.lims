from baobab.lims.utils.audit_logger import AuditLogger
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName

from baobab.lims.idserver import renameAfterCreation
from bika.lims.browser import BrowserView
from bika.lims.utils import tmpID
from baobab.lims.utils.send_email import send_email

import json

class AjaxCreateCollectionRequests(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):

        super(AjaxCreateCollectionRequests, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.collection_request = []
        self.errors = []

    def __call__(self):

        try:
            if 'collection_requests_data' not in self.request.form:
                raise Exception('No valid collection request samples data has been send')

            collection_request_data = json.loads(self.request.form['collection_requests_data'])
            collection_request_details = collection_request_data.get('collectionrequest_details', None)
            collection_request_human_samples = collection_request_data.get('human_collectionrequest_rows', None)
            collection_request_microbe_samples = collection_request_data.get('microbe_collectionrequest_rows', None)

            # process input and result samples
            collection_request_human_samples_results = self.create_collection_request_human_samples(
                collection_request_human_samples,
            )

            collection_request_microbe_samples_results = self.create_collection_request_microbe_samples(
                collection_request_microbe_samples,
            )
            collection_request_obj = self.create_collection_request_object(collection_request_details)

            for obj in collection_request_human_samples_results:
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)

            for obj in collection_request_microbe_samples_results:
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)

            collection_request_obj.getField("HumanSampleRequests").set(collection_request_obj, collection_request_human_samples_results)
            collection_request_obj.getField("MicrobeSampleRequests").set(collection_request_obj, collection_request_microbe_samples_results)
            collection_request_obj.unmarkCreationFlag()
            renameAfterCreation(collection_request_obj)

        except Exception as e:
            error_message = json.dumps({'error_message': str(e)})
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(500)
            self.request.RESPONSE.write(error_message)
        else:
            receiver = self.get_client_email_address(collection_request_obj)
            message = self.get_email_message()
            subject = 'Confirm reception of collection request'
            send_email(self.context, receiver, receiver, subject, message)

            audit_logger = AuditLogger(self.context, 'CollectionRequest')
            audit_logger.perform_simple_audit(collection_request_obj, 'New')

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

    def get_email_message(self):
        message = '''
        Dear Client
        
        Your request has been registered.  It is currently being analysed.  You will receive an email telling you the next steps to follow.  
        
        Best regards.
        From the Secretariat of BeReB IPCI
        '''

        return message

    def create_collection_request_object(self, collection_request_details):
        collection_requests = self.context.collection_requests
        obj = _createObjectByType('CollectionRequest', collection_requests, tmpID())
        client = self.get_content_type(collection_request_details['client'])

        obj.edit(
            Client=client,
            RequestNumber=collection_request_details['request_number'],
            DateOfRequest=collection_request_details['date_of_request'],
            # NumberRequested=collection_request_details['number_requested'],
            CollectHumanSamples=collection_request_details['collect_human_samples'],
            CollectMicrobeSamples=collection_request_details['collect_microbe_samples'],
        )

        return obj

    def create_collection_request_human_samples(self, collection_request_human_rows):

        collection_request_human_samples = []

        for row_data in collection_request_human_rows:
            collection_request_human_sample = self.create_human_sample_request(row_data)
            collection_request_human_samples.append(collection_request_human_sample)

        return collection_request_human_samples

    def create_collection_request_microbe_samples(self, collection_request_microbe_rows):

        collection_request_microbe_samples = []

        for row_data in collection_request_microbe_rows:
            collection_request_microbe_sample = self.create_microbe_sample_request(row_data)
            collection_request_microbe_samples.append(collection_request_microbe_sample)

        return collection_request_microbe_samples

    def create_human_sample_request(self, collection_request_microbe_sample):

        try:
            human_sample_requests = self.context.human_sample_requests
            sample_type = self.get_content_type(collection_request_microbe_sample.get('sample_type', 'unknown'))
            sample_package = self.get_content_type(collection_request_microbe_sample.get('sample_package', 'unknown'))
            obj = _createObjectByType('HumanSampleRequest', human_sample_requests, tmpID())

            obj.edit(
                Barcode=collection_request_microbe_sample['barcode'],
                SampleType=sample_type,
                SamplePackage=sample_package,
                Volume=collection_request_microbe_sample['volume'],
                Unit=collection_request_microbe_sample['unit'],
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

            return obj

        except Exception as e:
            return None

    def create_microbe_sample_request(self, collection_request_microbe_sample):

        try:
            microbe_sample_requests = self.context.microbe_sample_requests
            strain = self.get_content_type(collection_request_microbe_sample.get('strain', 'unknown'))
            sample_type = self.get_content_type(collection_request_microbe_sample.get('sample_type', 'unknown'))
            obj = _createObjectByType('MicrobeSampleRequest', microbe_sample_requests, tmpID())

            obj.edit(
                Identification=collection_request_microbe_sample['identification'],
                Strain=strain,
                Origin=collection_request_microbe_sample['origin'],
                SampleType=sample_type,
                Phenotype=collection_request_microbe_sample['phenotype'],
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

            return obj

        except Exception as e:
            print('---------create microbe sample request error')
            print(str(e))
            return None

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
