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

class AjaxReversePooling(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):

        super(AjaxReversePooling, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.portal_workflow = getToolByName(self.context, 'portal_workflow')
        self.pooling_results = []
        self.errors = []

    def __call__(self):

        try:
            if 'pooling_data' not in self.request.form:
                raise Exception('No valid sample pooling object data has been send to the server')

            pooling_data = json.loads(self.request.form['pooling_data'])
            print(pooling_data)
            pooling_obj = self.get_content_type(pooling_data['object_uid'])
            if not pooling_obj:
                raise Exception('Pooling object not found')

            input_samples = pooling_obj.getInputSamples()
            intermediate_sample = pooling_obj.getIntermediateSample()
            result_samples = pooling_obj.getResultSamples()

            poolings_url = pooling_obj.aq_parent.absolute_url()
            pooling_obj.aq_parent.manage_delObjects([pooling_obj.getId()])

            self.reverse_result_samples(result_samples)
            self.reverse_intermediate_sample(intermediate_sample)
            self.reverse_input_samples(input_samples)

            output = json.dumps({
                'url': poolings_url
            })

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(200)
            self.request.RESPONSE.write(output)

        except Exception as e:
            error_message = json.dumps({'error_message': str(e)})
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(500)
            self.request.RESPONSE.write(error_message)

    def reverse_result_samples(self, result_samples):
        for result_sample in result_samples:
            aliquot = result_sample.getFinalSample()
            result_sample.aq_parent.manage_delObjects([result_sample.getId()])

            storage_location = aliquot.getField('StorageLocation').get(aliquot)
            if storage_location:
                self.portal_workflow.doActionFor(storage_location, 'liberate')

            aliquot.aq_parent.manage_delObjects([aliquot.getId()])

    def reverse_intermediate_sample(self, intermediate_sample):
        storage_location = intermediate_sample.getStorageLocation()

        if storage_location:
            self.portal_workflow.doActionFor(storage_location, 'liberate')
        intermediate_sample.aq_parent.manage_delObjects([intermediate_sample.getId()])

    def reverse_input_samples(self, input_samples):
        for input_sample in input_samples:
            selected_sample = input_sample.getSelectedSample()
            self.restore_input_sample_volume(selected_sample, input_sample.getField('InputVolume').get(input_sample))
            input_sample.getField('SelectedSample').set(input_sample, None)
            input_sample.reindexObject()
            input_sample.aq_parent.manage_delObjects([input_sample.getId()])

    def restore_input_sample_volume(self, sample, volume):
        new_volume = float(str(sample.getField('Volume').get(sample))) + float(volume)
        sample.getField('Volume').set(sample, str(new_volume))
        sample.reindexObject()

    def get_content_type(self, content_type_uid):
        try:
            brains = self.pc(UID=content_type_uid)
            return brains[0].getObject()
        except Exception as e:
            return None