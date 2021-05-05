from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView

from Products.CMFPlone.utils import _createObjectByType
from baobab.lims.idserver import renameAfterCreation

from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor

import json

class AjaxRetrieveSavedAliquots(BrowserView):

    def __init__(self, context, request):
        super(AjaxRetrieveSavedAliquots, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.viral_genomic_analysis = []
        self.errors = []

    def __call__(self):

        try:

            if 'sample_aliquots' not in self.request.form:
                raise Exception('No valid extract genomic material data found')

            sample_aliquots_data = json.loads(self.request.form['sample_aliquots'])
            viral_genomic_analysis_uid = sample_aliquots_data.get('viral_genomic_analysis_uid', None)

            viral_genomic_analysis_obj = self.get_content_type(viral_genomic_analysis_uid)

            saved_aliquots = viral_genomic_analysis_obj.prepare_virus_aliquots()

        except Exception as e:
            error_message = json.dumps({'error_message': str(e)})

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(500)
            self.request.RESPONSE.write(error_message)
        else:
            output = json.dumps(
                saved_aliquots
            )

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(200)
            self.request.RESPONSE.write(output)

    def create_virus_aliquots(self, aliquot_rows):
        aliquots_data = aliquot_rows
        viral_aliquots = []

        for sample_uid, new_aliquots_data in aliquots_data.iteritems():
            aliquots = []

            try:
                sample = self.get_sample(sample_uid)
                if not sample:
                    self.sample_results.append('Sample with uid %s is not found' % sample_uid)
                    continue
                for aliquot_data in new_aliquots_data:

                    if not all(k in aliquot_data for k in ('volume', 'barcode')):
                        self.sample_results.append('Aliquot for sample %s is missing either barcode or volume' %sample.Title())
                        continue

                    try:
                        storage_brains = self.pc(portal_type='StoragePosition', UID=aliquot_data['storage'])
                        storage_location = storage_brains and storage_brains[0].getObject() or None
                        new_volume = float(str(sample.getField('Volume').get(sample))) - float(aliquot_data['volume'])

                        # New aliquot volume too large.  Dont create aliquote.  return a warning.
                        if new_volume < 0:
                            self.sample_results.append('Aliquot %s volume %s exceed remaining sample volume %s for sample %s'
                                                       % (aliquot_data['barcode'], aliquot_data['volume'],
                                                          sample.getField('Volume').get(sample), sample.Title()))
                            continue

                        new_aliquot = self.create_aliquot(sample, aliquot_data)
                        if new_aliquot:

                            # Subtract the new aliquot volume from the parent sample volume
                            sample.getField('Volume').set(sample, str(new_volume))
                            sample.reindexObject()

                            # Set the storage location for the new aliquot
                            new_aliquot.edit(
                                StorageLocation=storage_location
                            )

                            new_aliquot.reindexObject()
                            if storage_location:
                                doActionFor(storage_location, 'occupy')

                            aliquots.append(new_aliquot)

                    except Exception as e:
                        self.sample_results.append("Error creating aliquot with barcode %s and volume %s for sample %s."
                            % (aliquot_data['barcode'], aliquot_data['volume'], sample.Title()))
                        continue

                virus_aliquot = self.create_virus_aliquot(sample, aliquots)
                viral_aliquots.append(virus_aliquot)

            except Exception as e:
                self.sample_results.append('Exception occurred when creating aliquots.  %s' % str(e))
                continue

        return viral_aliquots

    def get_sample(self, sample_uid):
        # pc = getToolByName(self.context, 'portal_catalog')
        try:
            brains = self.pc(UID=sample_uid)
            return brains[0].getObject()
        except Exception as e:
            return None

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
            print(str(e))
            pass

    def create_aliquot(self, parent_sample,  aliquot):

        try:
            parent = parent_sample.aq_parent
            unit = parent_sample.getField('Unit').get(parent_sample)
            sample_type = parent_sample.getField('SampleType').get(parent_sample)

            obj = _createObjectByType('Sample', parent, tmpID())

            # Only change date created if a valid date created was send from client
            # If date created is there and time create is there as well create a date time object
            date_created = aliquot.get('datecreated', None)
            time_created = aliquot.get('timecreated', None)
            if date_created and time_created:
                date_created = date_created + ' ' + time_created
            if date_created:
                obj.edit(
                    DateCreated=date_created,
                )

            obj.edit(
                title=aliquot['barcode'],
                description='',
                Project=parent,
                DiseaseOntology=parent_sample.getField('DiseaseOntology').get(parent_sample),
                Donor=parent_sample.getField('Donor').get(parent_sample),
                SampleType=sample_type,
                SubjectID=parent_sample.getField('SubjectID').get(parent_sample),
                Barcode=aliquot['barcode'],
                Volume=aliquot['volume'],
                Unit=unit,
                SamplingDate=parent_sample.getField('SamplingDate').get(parent_sample),
                LinkedSample=parent_sample
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            return obj

        except Exception as e:
            return None


    # def process_extract_genomic_materials(self, extract_rows):
    #
    #     extract_objs = []
    #     for row in extract_rows:
    #         obj = self.create_extract_genomic_material_object(row)
    #         extract_objs.append(obj)
    #
    #     return extract_objs
    #
    # def create_extract_genomic_material_object(self, extract_item_data):
    #
    #     extract_genomic_materials = self.context.extract_genomic_materials
    #     obj = _createObjectByType('ExtractGenomicMaterial', extract_genomic_materials, tmpID())
    #     virus_sample = self.get_content_type(extract_item_data['virus_sample'])
    #     method = self.get_content_type(extract_item_data['method'])
    #
    #     obj.edit(
    #         title=extract_item_data['new_sample_barcode'],
    #         VirusSample=virus_sample,
    #         HeatInactivated=extract_item_data['heat_inactivated'],
    #         Method=method,
    #         ExtractionBarcode=extract_item_data['new_sample_barcode'],
    #         Volume=extract_item_data['new_sample_volume'],
    #         Unit=extract_item_data['new_sample_unit'],
    #         WasKitUsed=extract_item_data['kit_used'],
    #         KitNumber=extract_item_data['kit_number'],
    #         Notes=extract_item_data['notes'],
    #     )
    #
    #     # obj.unmarkCreationFlag()
    #     # renameAfterCreation(obj)
    #
    #     return obj

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
