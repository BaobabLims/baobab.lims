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


# class BatchBiospecimensView(BiospecimensView):
#     """ Biospecimens veiw from kit view.
#     """
#     def __init__(self, context, request):
#         BiospecimensView.__init__(self, context, request, 'batch')
#         self.context = context
#         self.context_actions = {}
#
#         # Filter biospecimens by project uid
#         self.columns.pop('Project', None)
#         # path = '/'.join(self.context.getPhysicalPath())
#         for state in self.review_states:
#             # state['contentFilter']['path'] = {'query': path, 'depth': 1}
#             state['contentFilter']['getProjectUID'] = self.context.aq_parent.UID()
#             state['contentFilter']['sort_on'] = 'sortable_title'
#             state['columns'].remove('Project')
#
#     def folderitems(self, full_objects=False):
#         items = BiospecimensView.folderitems(self)
#         out_items = []
#         for item in items:
#             if "obj" not in item:
#                 continue
#             obj = item['obj']
#             batch = obj.getField('Batch').get(obj)
#             if batch:
#                 batch_uid = batch.UID()
#                 if batch_uid == self.context.UID():
#                     out_items.append(item)
#         return out_items
#

class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/sample_pooling_edit.pt')

    def __call__(self):
        request = self.request
        context = self.context
        self.form = request.form


        if 'submitted' in request:
            # audit_logger = AuditLogger(self.context, 'batch')
            try:
                self.validate_form_input()
            except ValidationError as e:
                self.form_error(e.message)
                return

            context.setConstrainTypesMode(constraintypes.DISABLED)
            portal_factory = getToolByName(context, 'portal_factory')

            folder = context.aq_parent
            batch = None
            is_new = False
            if not folder.hasObject(context.getId()):
                is_new = True
                batch = portal_factory.doCreate(context, context.id)
            else:
                is_new = False
                batch = context
                # self.perform_batch_audit(batch, request)

            old_qty = int(batch.Quantity or 0)
            new_qty = int(self.form.get('Quantity', 0))
            batch.processForm()
            self.create_samples(batch, self.form, new_qty - old_qty)

            obj_url = batch.absolute_url_path()

            # if is_new:
            #     audit_logger.perform_simple_audit(batch, 'New')
            request.response.redirect(obj_url)

            return

        return self.template()

    def perform_batch_audit(self, batch, request):
        audit_logger = AuditLogger(self.context, 'batch')
        pc = getToolByName(self.context, "portal_catalog")

        if batch.getField('Title').get(batch) != request.form['Title']:
            audit_logger.perform_simple_audit(batch, 'Title', batch.getField('Title').get(batch),
                                              request.form['Title'])

        if batch.getField('BatchID').get(batch) != request.form['BatchID']:
            audit_logger.perform_simple_audit(batch, 'BatchID', batch.getField('BatchID').get(batch),
                                              request.form['BatchID'])

        if batch.getField('Description').get(batch) != request.form['Description']:
            audit_logger.perform_simple_audit(batch, 'Description', batch.getField('Description').get(batch),
                                              request.form['Description'])

        if batch.getField('Quantity').get(batch) != request.form['Quantity']:
            audit_logger.perform_simple_audit(batch, 'Quantity', batch.getField('Quantity').get(batch),
                                              request.form['Quantity'])

        if not batch.getField('DateCreated').get(batch):
            audit_logger.perform_simple_audit(batch, 'DateCreated', batch.getField('DateCreated').get(batch), str(DateTime()))

    def validate_form_input(self):
        new_qty = int(self.form.get('Quantity', 0))
        old_qty = int(self.context.Quantity or 0)

        if new_qty <= 0:
            raise ValidationError('Quantity of samples cannot be zero or less than zero!')
        if new_qty < old_qty:
            raise ValidationError('New number of samples cannot be less than the number of samples already created!')

    def create_samples(self, context, form, num_samples):
        """Create samples from form
        """
        sample_type = get_first_sampletype(context)
        uc = getToolByName(context, 'uid_catalog')

        project_uid = form.get('Project_uid', '')
        project = uc(UID=project_uid)[0].getObject()

        samples_gen = SampleGeneration(form, project)

        samples = []
        for i in range(num_samples):
            sample = samples_gen.create_sample(None, sample_type, context)
            samples.append(sample)

        location_uid = form.get('StorageLocation_uid', '')
        storage = []
        if location_uid:
            location = uc(UID=location_uid)[0].getObject()
            if len(location.get_free_positions()) > 0:
                storage.append(location)

        if storage:
            samples_gen.store_samples(samples, storage)

        return samples

    def get_fields_with_visibility(self, visibility, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:
                fields.append(field)
        return fields

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())


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
        try:
            pooling_data = self.request.form['pooling_data']
            pooling_data = json.loads(pooling_data)
        except:
            return json.dumps(self.pooling_results.append('No valid sample aliquots has been send to the server'))

        # Create sample pooling object
        poolings = self.context.sample_poolings
        obj = _createObjectByType('SamplePooling', poolings, tmpID())
        obj.edit(
            title='Test Title',
            description='This is a test description',
        )
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)

        # Subtract the units from the input samples
        input_samples = pooling_data['input_samples_data']
        self.process_input_samples(obj, input_samples)

        # Create the new aliquot samples from the pools
        aliquot_samples = pooling_data['aliquots_data']
        self.process_result_samples(obj, aliquot_samples)

    def process_input_samples(self, sample_pooling, input_samples):

        for input_sample in input_samples:

            sample = self.get_sample(input_sample['sample'])
            self.adjust_input_sample_volume(sample)
            self.create_pooling_input(sample_pooling, input_sample, sample)


    def create_pooling_input(self, sample_pooling, input_sample_data, sample):

        input_sample = api.content.create(
            container=sample_pooling,
            type="ResultSample",
            id=tmpID(),
            title='result_sample' + datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f'),
            FinalSample=sample,
            FinalVolume=input_sample_data['volume'],
            FinalUnit=input_sample_data['unit'],
        )

        input_sample.reindexObject()

    def adjust_input_sample_volume(self, sample, volume):

        new_volume = float(str(sample.getField('Volume').get(sample))) - float(volume)
        if new_volume < 0:
            raise Exception('New volume too low')

        sample.getField('Volume').set(sample, str(new_volume))
        sample.reindexObject()

    def process_result_samples(self, sample_pooling, aliquot_samples):

        for aliquot_sample in aliquot_samples:

            aliquot = self.create_aliquot(aliquot_sample)

            # Create ResultSample Object
            result_sample = api.content.create(
                container=sample_pooling,
                type="InputSample",
                id=tmpID(),
                title='input_sample' + datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f'),
                SelectedSample=aliquot
            )
            result_sample.reindexObject()

    def create_aliquot(self, aliquot_data):

        try:
            # parent = parent_sample.aq_parent
            # unit = parent_sample.getField('Unit').get(parent_sample)
            # sample_type = parent_sample.getField('SampleType').get(parent_sample)
            project = self.get_project()

            obj = _createObjectByType('Sample', project, tmpID())

            # Only change date created if a valid date created was send from client
            # If date created is there and time create is there as well create a date time object
            # date_created = aliquot.get('datecreated', None)
            # time_created = aliquot.get('timecreated', None)
            # if date_created and time_created:
            #     date_created = date_created + ' ' + time_created
            # if date_created:
            #     obj.edit(
            #         DateCreated=date_created,
            #     )

            # project = self.get_project()
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


