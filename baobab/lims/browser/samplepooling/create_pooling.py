from zope.schema import ValidationError

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.lib import constraintypes
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName

from baobab.lims.browser.project.util import SampleGeneration
from baobab.lims.browser.project import get_first_sampletype
from baobab.lims.browser.biospecimens.biospecimens import BiospecimensView
from baobab.lims.idserver import renameAfterCreation

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

    def __call__(self):
        # print('===================')
        # print('Inside create sample poolings')
        # print(self.request.form)
        try:
            pooling_data = self.request.form['pooling_data']
            pooling_data = json.loads(pooling_data)
        except Exception as e:
            return json.dumps(self.pooling_results.append('No valid sample aliquots has been send to the server'))

        pooling_obj = self.create_sample_pooling_object(pooling_data['sample_pooling_data'])

        # process input and result samples
        input_samples = self.process_input_samples(pooling_data['input_samples_data'], pooling_obj)
        result_samples = self.process_result_samples(pooling_data['aliquots_data'])

        pooling_obj.getField("InputSamples").set(pooling_obj, input_samples)
        pooling_obj.getField("ResultSamples").set(pooling_obj, result_samples)

        pooling_obj.unmarkCreationFlag()
        renameAfterCreation(pooling_obj)

        print('---------------The redirect happens here.')
        print(pooling_obj.absolute_url())
        self.request.response.redirect(pooling_obj.absolute_url())

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

    def process_input_samples(self, input_samples_data, pooling_obj):

        input_samples = []

        for input_sample_data in input_samples_data:

            sample = self.get_sample(input_sample_data['sample'])
            self.adjust_input_sample_volume(sample, input_sample_data['volume'])
            input_sample = self.create_pooling_input(input_sample_data, sample, pooling_obj)
            input_samples.append(input_sample)

        return input_samples

    def create_pooling_input(self, input_sample_data, sample, pooling_obj):
        folder = self.context.inputsamples

        input_sample = api.content.create(
            container=folder,
            type="InputSample",
            id=tmpID(),
            title='input_sample' + datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f'),
            # SelectedSample=sample,
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
                FinalUnit=aliquot_sample_data['unit'],
            )

            result_sample.getField('FinalSample').set(result_sample, aliquot)
            print(result_sample.__dict__)

            result_sample.reindexObject()
            result_samples.append(result_sample)
            print(result_sample.__dict__)

        return result_samples

    def create_aliquot(self, aliquot_data):

        try:
            project = self.get_project()

            obj = _createObjectByType('Sample', project, tmpID())

            sample_type = self.get_sample_type()

            obj.edit(
                title=aliquot_data['barcode'],
                description='',
                Project=project,
                # DiseaseOntology=parent_sample.getField('DiseaseOntology').get(parent_sample),
                # Donor=parent_sample.getField('Donor').get(parent_sample),
                SampleType=sample_type,
                # SubjectID=parent_sample.getField('SubjectID').get(parent_sample),
                Barcode=aliquot_data['barcode'],
                Volume=aliquot_data['volume'],
                Unit=aliquot_data['unit'],
                # SamplingDate=parent_sample.getField('SamplingDate').get(parent_sample),
                # LinkedSample=parent_sample
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            return obj

        except Exception as e:
            return None






        # for sample_uid, new_aliquots in aliquots_data.iteritems():
        #
        #     try:
        #         sample = self.get_sample(sample_uid)
        #         if not sample:
        #             self.sample_results.append('Sample with uid %s is not found' % sample_uid)
        #             continue
        #         for aliquot in new_aliquots:
        #             if not all(k in aliquot for k in ('volume', 'barcode')):
        #                 self.sample_results.append('Aliquot for sample %s is missing either barcode or volume' %sample.Title())
        #                 continue
        #
        #             try:
        #                 storage_brains = self.pc(portal_type='StoragePosition', UID=aliquot['storage'])
        #                 storage_location = storage_brains and storage_brains[0].getObject() or None
        #                 new_volume = float(str(sample.getField('Volume').get(sample))) - float(aliquot['volume'])
        #                 # New aliquot volume too large.  Dont create aliquote.  return a warning.
        #                 if new_volume < 0:
        #                     self.sample_results.append('Aliquot %s volume %s exceed remaining sample volume %s for sample %s'
        #                                                % (aliquot['barcode'], aliquot['volume'],
        #                                                   sample.getField('Volume').get(sample), sample.Title()))
        #                     continue
        #
        #                 new_aliquot = self.create_aliquot(sample, aliquot)
        #                 if new_aliquot:
        #                     # Subtract the new aliquot volume from the parent sample volume
        #                     sample.getField('Volume').set(sample, str(new_volume))
        #                     sample.reindexObject()
        #
        #                     # Set the storage location for the new aliquot
        #                     new_aliquot.edit(
        #                         StorageLocation=storage_location
        #                     )
        #
        #                     new_aliquot.reindexObject()
        #                     if storage_location:
        #                         doActionFor(storage_location, 'occupy')
        #
        #                     self.sample_results.append('Successfully created aliquot with barcode %s and volume %s for sample %s'
        #                                           % (aliquot['barcode'], aliquot['volume'], sample.Title()))
        #
        #             except Exception as e:
        #                 # print('------------Exception on aliquot create')
        #                 # print(str(e))
        #                 self.sample_results.append("Error creating aliquot with barcode %s and volume %s for sample %s."
        #                     % (aliquot['barcode'], aliquot['volume'], sample.Title()))
        #                 continue
        #
        #     except Exception as e:
        #         self.sample_results.append('Exception occurred when creating aliquots.  %s' % str(e))
        #         continue
        #
        # return json.dumps(self.sample_results)

    def get_sample(self, sample_uid):
        # pc = getToolByName(self.context, 'portal_catalog')
        try:
            brains = self.pc(UID=sample_uid)
            return brains[0].getObject()
        except Exception as e:
            return None

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

    # def create_aliquot(self, parent_sample,  aliquot):
    #
    #     try:
    #         parent = parent_sample.aq_parent
    #         unit = parent_sample.getField('Unit').get(parent_sample)
    #         sample_type = parent_sample.getField('SampleType').get(parent_sample)
    #
    #         obj = _createObjectByType('Sample', parent, tmpID())
    #
    #         # Only change date created if a valid date created was send from client
    #         # If date created is there and time create is there as well create a date time object
    #         date_created = aliquot.get('datecreated', None)
    #         time_created = aliquot.get('timecreated', None)
    #         if date_created and time_created:
    #             date_created = date_created + ' ' + time_created
    #         if date_created:
    #             obj.edit(
    #                 DateCreated=date_created,
    #             )
    #
    #         obj.edit(
    #             title=aliquot['barcode'],
    #             description='',
    #             Project=parent,
    #             DiseaseOntology=parent_sample.getField('DiseaseOntology').get(parent_sample),
    #             Donor=parent_sample.getField('Donor').get(parent_sample),
    #             SampleType=sample_type,
    #             SubjectID=parent_sample.getField('SubjectID').get(parent_sample),
    #             Barcode=aliquot['barcode'],
    #             Volume=aliquot['volume'],
    #             Unit=unit,
    #             SamplingDate=parent_sample.getField('SamplingDate').get(parent_sample),
    #             LinkedSample=parent_sample
    #         )
    #
    #         obj.unmarkCreationFlag()
    #         renameAfterCreation(obj)
    #         return obj
    #
    #     except Exception as e:
    #         return None


