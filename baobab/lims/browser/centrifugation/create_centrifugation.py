from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from baobab.lims.idserver import renameAfterCreation

from baobab.lims.utils.audit_logger import AuditLogger
from bika.lims.browser import BrowserView
from bika.lims.workflow import doActionFor
from bika.lims.utils import tmpID

import json
import plone.protect

class AjaxCreateCentrifugations(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):

        super(AjaxCreateCentrifugations, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.pooling_results = []
        self.errors = []

    def __call__(self):

        try:
            # plone.protect.CheckAuthenticator(self.request.form)

            if 'centrifugation_data' not in self.request.form:
                raise Exception('No valid sample centrifugation data has been send')
            print(self.request.form['centrifugation_data'])

            centrifugation_data = json.loads(self.request.form['centrifugation_data'])
            centrifugation_rows = centrifugation_data.get('centrifugation_rows', None)
            centrifugation_details = centrifugation_data.get('centrifugation_details', None)

            # process input and result samples
            centrifugation_rows_results = self.create_centrifugation_rows(centrifugation_rows, centrifugation_details['selectedsample'])
            centrifugation_obj = self.create_sample_centrifugation_object(centrifugation_details)

            for obj in centrifugation_rows_results:
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)

            centrifugation_obj.getField("Centrifuges").set(centrifugation_obj, centrifugation_rows_results)
            centrifugation_obj.unmarkCreationFlag()
            renameAfterCreation(centrifugation_obj)

        except Exception as e:
            error_message = json.dumps({'error_message': str(e)})
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(500)
            self.request.RESPONSE.write(error_message)
        else:
            audit_logger = AuditLogger(self.context, 'Centrifugation')
            audit_logger.perform_simple_audit(centrifugation_obj, 'New')
            output = json.dumps({
                'url': centrifugation_obj.absolute_url()
            })

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(200)
            self.request.RESPONSE.write(output)

    def create_sample_centrifugation_object(self, centrifugation_details):
        centrifugations = self.context.centrifugations
        obj = _createObjectByType('Centrifugation', centrifugations, tmpID())
        selectedsample = self.get_content_type(centrifugation_details['selectedsample'])
        technician = self.get_content_type(centrifugation_details['technician'])

        obj.edit(
            title=centrifugation_details['title'],
            description=centrifugation_details['description'],
            SelectedSample=selectedsample,
            DateCreated=centrifugation_details['date_created'],
            Technician=technician,
            Technique=centrifugation_details['technique'],
        )

        return obj

    def create_centrifugation_rows(self, centrifugation_rows, selected_sample):

        centrifugation_samples = []

        for row_data in centrifugation_rows:
            centrifugation_sample = self.create_aliquot(row_data, selected_sample)
            centrifugation_samples.append(centrifugation_sample)

        return centrifugation_samples

    def create_aliquot(self, aliquot_data, selected_sample):

        try:
            storage_location = self.get_content_type(aliquot_data.get('storageposition', 'unknown'))

            project = self.get_project(selected_sample)
            sample_type = self.get_content_type(aliquot_data.get('project', 'unknown'))
            obj = _createObjectByType('Sample', project, tmpID())
            sample_condition = self.get_content_type(aliquot_data.get('condition', 'unknown'), 'bika_setup_catalog')

            obj.edit(
                title=aliquot_data['barcode'],
                description='',
                Project=project,
                SampleCondition=sample_condition,
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

            if storage_location:
                doActionFor(storage_location, 'occupy')

            return obj

        except Exception as e:
            # print('---------create aliquot error')
            # print(str(e))
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

    # def get_sample_type(self, sample_type_uid='8f255d3f572540db840decf059ead122'):
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