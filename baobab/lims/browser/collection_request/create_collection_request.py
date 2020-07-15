from zope.schema import ValidationError
from zope.schema import ValidationError

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.lib import constraintypes
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName

from baobab.lims.browser.project.util import SampleGeneration
from baobab.lims.browser.project import get_first_sampletype
from baobab.lims.browser.biospecimens.biospecimens import BiospecimensView
from baobab.lims.idserver import renameAfterCreation

from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime
from bika.lims.browser import BrowserView
from bika.lims.workflow import doActionFor
from bika.lims.utils import tmpID

import json
from plone import api
from datetime import datetime

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
            # raise Exception('This is an exception from Plone.')
            print('-------------This is Collection Requests')

            if 'collection_requests_data' not in self.request.form:
                raise Exception('No valid collection request samples data has been send')

            collection_request_data = json.loads(self.request.form['collection_requests_data'])
            collection_request_details = collection_request_data.get('collectionrequest_details', None)
            collection_request_human_samples = collection_request_data.get('human_collectionrequest_rows', None)
            collection_request_microbe_samples = collection_request_data.get('microbe_collectionrequest_rows', None)

            # process input and result samples
            collection_request_human_samples_results = self.create_collection_request_human_samples(
                collection_request_human_samples,
                # collection_request_details
            )
            collection_request_microbe_samples_results = self.create_collection_request_microbe_samples(
                collection_request_microbe_samples,
                # collection_request_details
            )
            collection_request_obj = self.create_collection_request_object(collection_request_details)
            # print('-----------------This is the collection request')
            # print(collection_request_human_samples_results)
            # print(collection_request_microbe_samples_results)
            # print(collection_request_obj.__dict__)
            # raise Exception('This is the exception for collection request')

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

            # print('---------------complete Correction Request')
            # print(collection_request_obj.__dict__)

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

    def create_collection_request_object(self, collection_request_details):
        collection_requests = self.context.collection_requests
        obj = _createObjectByType('CollectionRequest', collection_requests, tmpID())
        client = self.get_content_type(collection_request_details['client'])
        sample_kingdom = self.get_content_type(collection_request_details['sample_kingdom'])


        obj.edit(
            # title=collection_request_details['title'],
            # description=collection_request_details['description'],
            Client=client,
            RequestNumber=collection_request_details['request_number'],
            # DateOfRequest=collection_request_details['date_of_request'],
            SampleKingdom=sample_kingdom,
            NumberRequested=collection_request_details['number_requested'],
            # DateEvaluated=collection_request_details['date_evaluated'],
            # ResultOfEvaluation=collection_request_details['result_of_evaluation'],
            # ReasonForEvaluation=collection_request_details['reason_for_evaluation'],
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
            obj = _createObjectByType('HumanSampleRequest', human_sample_requests, tmpID())

            obj.edit(
                Barcode=collection_request_microbe_sample['barcode'],
                SampleType=sample_type,
                Volume=collection_request_microbe_sample['volume'],
                Unit=collection_request_microbe_sample['unit'],
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

            return obj

        except Exception as e:
            print('---------create human sample request error')
            print(str(e))
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
