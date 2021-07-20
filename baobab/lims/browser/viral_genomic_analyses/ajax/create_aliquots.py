from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView

from Products.CMFPlone.utils import _createObjectByType
from baobab.lims.idserver import renameAfterCreation

from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor

import json

from baobab.lims.utils.retrieve_objects import get_object_from_uid

class AjaxCreateVirusSampleAliquots(BrowserView):

    def __init__(self, context, request):
        super(AjaxCreateVirusSampleAliquots, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.viral_genomic_analysis = []
        self.errors = []
        self.sample_results = []

    def __call__(self):

        try:

            if 'sample_aliquots' not in self.request.form:
                raise Exception('No valid extract genomic material data found')

            sample_aliquots_data = json.loads(self.request.form['sample_aliquots'])
            viral_genomic_analysis_uid = sample_aliquots_data.get('viral_genomic_analysis_uid', None)
            sample_aliquot_rows = sample_aliquots_data.get('sample_aliquot_rows', None)

            viral_genomic_analysis_obj = self.get_content_type(viral_genomic_analysis_uid)
            viral_aliquots = self.create_virus_aliquots(sample_aliquot_rows)

            if self.errors:
                raise Exception('Errors creating virus aliquots')

            viral_genomic_analysis_obj.getField('VirusAliquot').set(viral_genomic_analysis_obj, viral_aliquots)
            viral_genomic_analysis_obj.reindexObject()

        except Exception as e:
            error_message = json.dumps({'error_message': self.errors})
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(500)
            self.request.RESPONSE.write(error_message)
        else:
            output = json.dumps({
                'url': viral_genomic_analysis_obj.absolute_url()
            })

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(200)
            self.request.RESPONSE.write(output)

    def create_virus_aliquots(self, aliquot_rows):
        aliquots_data = aliquot_rows
        viral_aliquots = []

        for virus_sample_uid, new_aliquots_data in aliquots_data.iteritems():
            aliquots = []

            try:
                virus_sample = get_object_from_uid(self.context, virus_sample_uid)
                if not virus_sample:
                    self.errors.append('Sample with uid %s is not found' % virus_sample_uid)
                    continue
                for aliquot_data in new_aliquots_data:

                    if not all(k in aliquot_data for k in ('volume', 'barcode')):
                        self.errors.append('Aliquot for sample %s is missing either barcode or volume' % virus_sample.getField('Barcode').get(virus_sample))
                        continue

                    try:
                        storage_brains = self.pc(portal_type='StoragePosition', UID=aliquot_data['storage'])
                        storage_location = storage_brains and storage_brains[0].getObject() or None
                        new_volume = float(str(virus_sample.getField('Volume').get(virus_sample))) - float(aliquot_data['volume'])

                        # New aliquot volume too large.  Dont create aliquote.  return a warning.
                        if new_volume < 0:
                            self.errors.append('Aliquot %s volume %s exceed remaining sample volume %s for sample %s'
                                                       % (aliquot_data['barcode'], aliquot_data['volume'],
                                                          virus_sample.getField('Volume').get(virus_sample),
                                                          virus_sample.getField('Barcode').get(virus_sample)))
                            continue

                        new_aliquot = self.create_aliquot(virus_sample, aliquot_data)
                        if new_aliquot:

                            # Subtract the new aliquot volume from the parent sample volume
                            virus_sample.getField('Volume').set(virus_sample, str(new_volume))
                            virus_sample.reindexObject()

                            # Set the storage location for the new aliquot
                            new_aliquot.edit(
                                StorageLocation=storage_location
                            )

                            new_aliquot.reindexObject()
                            if storage_location:
                                doActionFor(storage_location, 'occupy')

                            aliquots.append(new_aliquot)

                    except Exception as e:
                        self.errors.append("Error creating aliquot with barcode %s and volume %s for sample %s."
                            % (aliquot_data['barcode'], aliquot_data['volume'],
                               virus_sample.getField('Barcode').get(virus_sample)))
                        continue

                virus_aliquot = self.create_virus_aliquot(virus_sample, aliquots)
                viral_aliquots.append(virus_aliquot)

            except Exception as e:
                self.errors.append('Exception occurred when creating aliquots.  %s' % str(e))
                continue

        return viral_aliquots

    def create_virus_aliquot(self, parent_sample, aliquots):

        try:

            virus_aliquots = self.context.virus_aliquots
            obj = _createObjectByType('VirusAliquot', virus_aliquots, tmpID())

            obj.edit(
                ParentSample=parent_sample,
                AliquotSample=aliquots,
            )

            obj.unmarkCreationFlag()
            obj.reindexObject()

            return obj

        except Exception as e:
            pass

    def create_aliquot(self, parent_sample,  aliquot):

        try:
            # parent_project = parent_sample.aq_parent
            folder = self.context.virus_samples
            unit = parent_sample.getField('Unit').get(parent_sample)
            sample_type = parent_sample.getField('SampleType').get(parent_sample)
            project = parent_sample.getProject()
            obj = _createObjectByType('VirusSample', folder, tmpID())

            # Only change date created if a valid date created was send from client
            # If date created is there and time create is there as well create a date time object
            date_created = aliquot.get('datecreated', None)
            time_created = aliquot.get('timecreated', None)
            if date_created and time_created:
                date_time_created = date_created + ' ' + time_created
            else:
                date_time_created = ''

            obj.edit(
                title=aliquot['barcode'],
                description='',
                # Project=parent_sample.getField('Project').get(parent_sample),
                Project=project,
                # DiseaseOntology=parent_sample.getField('DiseaseOntology').get(parent_sample),
                # Donor=parent_sample.getField('Donor').get(parent_sample),
                SampleType=sample_type,
                # SubjectID=parent_sample.getField('SubjectID').get(parent_sample),
                Barcode=aliquot['barcode'],
                DateCreated=date_time_created,
                Volume=aliquot['volume'],
                Unit=unit,
                SampleCollectionDate=parent_sample.getField('SampleCollectionDate').get(parent_sample),
                ParentSample=parent_sample
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

            # from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
            # ObjectInitializedEventHandler(obj, None)
            return obj

        except Exception as e:
            print('--------- %s' % str(e))
            self.errors.append(str(e))
            return None

    def get_content_type(self, content_type_uid, catalog="portal_catalog"):
        try:
            catalog = self.get_catalog(catalog)
            brains = catalog(UID=content_type_uid)
            return brains[0].getObject()
        except Exception as e:
            self.errors.append(str(e))
            return None

    def get_catalog(self, catalog="portal_catalog"):
        try:
            return getToolByName(self.context, catalog)
        except:
            return None
