import json
from operator import itemgetter

import plone
from baobab.lims.idserver import renameAfterCreation

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from bika.lims.browser import BrowserView
from bika.lims.utils import tmpID


class AjaxCreateExtractGenomicMaterial(BrowserView):

    def __init__(self, context, request):
        super(AjaxCreateExtractGenomicMaterial, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.viral_genomic_analysis = []
        self.errors = []

    def __call__(self):

        try:
            if 'extract_genomic_material' not in self.request.form:
                raise Exception('No valid extract genomic material data found')

            extract_genomic_material_data = json.loads(self.request.form['extract_genomic_material'])
            viral_genomic_analysis_uid = extract_genomic_material_data.get('viral_genomic_analysis_uid', None)
            extract_rows = extract_genomic_material_data.get('extract_genomic_material_rows', None)

            viral_genomic_analysis_obj = self.get_content_type(viral_genomic_analysis_uid)
            extract_genomic_material_objs = self.process_extract_genomic_materials(extract_rows)

            for obj in extract_genomic_material_objs:
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)

            viral_genomic_analysis_obj.getField('ExtractGenomicMaterial').set(viral_genomic_analysis_obj, extract_genomic_material_objs)
            viral_genomic_analysis_obj.reindexObject()

        except Exception as e:
            error_message = json.dumps({'error_message': str(e)})
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(500)
            self.request.RESPONSE.write(error_message)
        else:
            output = json.dumps ({
                'url': viral_genomic_analysis_obj.absolute_url()
            })

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(200)
            self.request.RESPONSE.write(output)

    def process_extract_genomic_materials(self, extract_rows):

        extract_objs = []
        for row in extract_rows:
            obj = self.create_extract_genomic_material_object(row)
            extract_objs.append(obj)

        return extract_objs

    def create_extract_genomic_material_object(self, extract_item_data):

        extract_genomic_materials = self.context.extract_genomic_materials
        obj = _createObjectByType('ExtractGenomicMaterial', extract_genomic_materials, tmpID())
        virus_sample = self.get_content_type(extract_item_data['virus_sample'])
        method = self.get_content_type(extract_item_data['method'])

        obj.edit(
            title=extract_item_data['new_sample_barcode'],
            VirusSample=virus_sample,
            HeatInactivated=extract_item_data['heat_inactivated'],
            Method=method,
            ExtractionBarcode=extract_item_data['new_sample_barcode'],
            Volume=extract_item_data['new_sample_volume'],
            Unit=extract_item_data['new_sample_unit'],
            WasKitUsed=extract_item_data['kit_used'],
            KitNumber=extract_item_data['kit_number'],
            Notes=extract_item_data['notes'],
        )

        # obj.unmarkCreationFlag()
        # renameAfterCreation(obj)

        return obj

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
