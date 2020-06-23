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

class AjaxCreatePoolings(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):

        super(AjaxCreatePoolings, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.pooling_results = []
        self.errors = []

    def __call__(self):

        try:
            # raise Exception('This is an exception from Plone.')
            if 'pooling_data' not in self.request.form:
                raise Exception('No valid sample pooling data has been send to the server')

            pooling_data = json.loads(self.request.form['pooling_data'])

            # process input and result samples
            intermediate_data = pooling_data.get('intermediate_sample_data', None)
            intermediate_sample = self.process_intermediate_sample(intermediate_data)

            input_samples = self.process_input_samples(pooling_data['input_samples_data'])
            result_samples = self.process_result_samples(pooling_data['aliquots_data'])

            pooling_obj = self.create_sample_pooling_object(pooling_data['sample_pooling_data'])
            pooling_obj.getField("InputSamples").set(pooling_obj, input_samples)
            pooling_obj.getField("IntermediateSample").set(pooling_obj, intermediate_sample)
            pooling_obj.getField("ResultSamples").set(pooling_obj, result_samples)
            pooling_obj.unmarkCreationFlag()
            renameAfterCreation(pooling_obj)

            output = json.dumps({
                'url': pooling_obj.absolute_url()
            })

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(200)
            self.request.RESPONSE.write(output)

        except Exception as e:
            error_message = json.dumps({'error_message': str(e)})
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(500)
            self.request.RESPONSE.write(error_message)

    def create_sample_pooling_object(self, sample_pooling_data):
        poolings = self.context.sample_poolings
        obj = _createObjectByType('SamplePooling', poolings, tmpID())
        obj.edit(
            title=sample_pooling_data['title'],
            description=sample_pooling_data['description'],
            DateCreated=sample_pooling_data['date_created'],
            PersonPooling=sample_pooling_data['person_pooling'],
        )

        return obj

    def process_input_samples(self, input_samples_data):

        input_samples = []

        for input_sample_data in input_samples_data:

            sample = self.get_sample(input_sample_data['sample'])
            self.adjust_input_sample_volume(sample, input_sample_data['volume'])
            input_sample = self.create_pooling_input(input_sample_data, sample)
            input_samples.append(input_sample)

        return input_samples

    def process_intermediate_sample(self, intermediate_sample_data):

        if not intermediate_sample_data:
            return
        try:
            storage_brains = self.pc(portal_type='StoragePosition', UID=intermediate_sample_data.get('storage', 'unknown'))
            storage_location = storage_brains and storage_brains[0].getObject() or None
            project = self.get_content_type(intermediate_sample_data.get('project', 'unknown'))
            obj = _createObjectByType('Sample', project, tmpID())
            sample_type = self.get_content_type(intermediate_sample_data.get('sampletype', 'unknown'))
            obj.edit(
                title=intermediate_sample_data['barcode'],
                description='',
                Project=project,
                SampleType=sample_type,
                Barcode=intermediate_sample_data['barcode'],
                Volume=intermediate_sample_data['volume'],
                Unit=intermediate_sample_data['unit'],
                StorageLocation=storage_location,
                # SubjectID=parent_sample.getField('SubjectID').get(parent_sample),
                # DiseaseOntology=parent_sample.getField('DiseaseOntology').get(parent_sample),
                # Donor=parent_sample.getField('Donor').get(parent_sample),
                # SamplingDate=parent_sample.getField('SamplingDate').get(parent_sample),
                # LinkedSample=parent_sample
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            ObjectInitializedEventHandler(obj, None)
            if storage_location:
                doActionFor(storage_location, 'occupy')
            return obj

        except Exception as e:
            return None

    def create_pooling_input(self, input_sample_data, sample):
        folder = self.context.inputsamples

        input_sample = api.content.create(
            container=folder,
            type="InputSample",
            id=tmpID(),
            title='input_sample' + datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f'),
            InputVolume=input_sample_data['volume'],
            # InputVolumeUnit=input_sample_data['unit'],
        )

        input_sample.getField('SelectedSample').set(input_sample, sample)

        input_sample.reindexObject()
        return input_sample

    def adjust_input_sample_volume(self, sample, volume):

        new_volume = float(str(sample.getField('Volume').get(sample))) - float(volume)
        if new_volume < 0:
            raise Exception('New volume too low')

        sample.getField('Volume').set(sample, str(new_volume))
        sample.reindexObject()

    def process_result_samples(self, aliquot_samples):

        result_samples = []
        folder = self.context.resultsamples

        for aliquot_sample_data in aliquot_samples:

            aliquot = self.create_aliquot(aliquot_sample_data)

            # Create ResultSample Object
            result_sample = api.content.create(
                container=folder,
                type="ResultSample",
                id=tmpID(),
                title='result_sample' + datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f'),
                FinalVolume=aliquot_sample_data['volume'],
                FinalVolumeUnit=aliquot_sample_data['unit'],
            )

            result_sample.getField('FinalSample').set(result_sample, aliquot)
            print(result_sample.__dict__)

            result_sample.reindexObject()
            result_samples.append(result_sample)
            print(result_sample.__dict__)

        return result_samples

    def create_aliquot(self, aliquot_data):

        try:
            storage_brains = self.pc(portal_type='StoragePosition', UID=aliquot_data.get('storage', 'unknown'))
            storage_location = storage_brains and storage_brains[0].getObject() or None

            project = self.get_content_type(aliquot_data.get('project', 'unknown'))
            sample_type = self.get_content_type(aliquot_data.get('project', 'unknown'))
            obj = _createObjectByType('Sample', project, tmpID())

            obj.edit(
                title=aliquot_data['barcode'],
                description='',
                Project=project,
                SampleType=sample_type,
                Barcode=aliquot_data['barcode'],
                Volume=aliquot_data['volume'],
                Unit=aliquot_data['unit'],
                StorageLocation=storage_location,
                # Donor=parent_sample.getField('Donor').get(parent_sample),
                # DiseaseOntology=parent_sample.getField('DiseaseOntology').get(parent_sample),
                # SubjectID=parent_sample.getField('SubjectID').get(parent_sample),
                # SamplingDate=parent_sample.getField('SamplingDate').get(parent_sample),
                # LinkedSample=parent_sample
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

            if storage_location:
                doActionFor(storage_location, 'occupy')

            return obj

        except Exception as e:
            return None

    def get_sample(self, sample_uid):
        # pc = getToolByName(self.context, 'portal_catalog')
        try:
            brains = self.pc(UID=sample_uid)
            return brains[0].getObject()
        except Exception as e:
            raise Exception('Sample to be pooled not found')

    def get_project(self):
        # pc = getToolByName(self.context, 'portal_catalog')
        try:
            brains = self.pc(title='Green Goblin Project')
            return brains[0].getObject()
        except Exception as e:
            return None

    def get_sample_type(self, sample_type_uid='8f255d3f572540db840decf059ead122'):
        # pc = getToolByName(self.context, 'portal_catalog')
        try:
            brains = self.pc(UID=sample_type_uid)
            return brains[0].getObject()
        except Exception as e:
            return None

    def get_content_type(self, content_type_uid):
        # pc = getToolByName(self.context, 'portal_catalog')
        try:
            brains = self.pc(UID=content_type_uid)
            return brains[0].getObject()
        except Exception as e:
            return None
