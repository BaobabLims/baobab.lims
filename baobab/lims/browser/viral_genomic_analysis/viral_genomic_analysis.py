# import os
# import traceback

from DateTime import DateTime
from Products.ATContentTypes.lib import constraintypes
# from Products.Archetypes.public import BaseFolder
from Products.CMFCore.utils import getToolByName
# from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone.app.content.browser.interfaces import IFolderContentsView
# from plone.app.layout.globals.interfaces import IViewView
# from zope.interface import implements

#from Products.Five.browser import BrowserView
from bika.lims.browser import BrowserView
# from bika.lims.browser.bika_listing import BikaListingView
# from bika.lims.browser.multifile import MultifileView
# from bika.lims.utils import to_utf8
# from baobab.lims import bikaMessageFactory as _
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime


class ViralGenomicAnalysisView(BrowserView):
    template = ViewPageTemplateFile('templates/viral_genomic_analysis_view.pt')

    def __init__(self, context, request):
        super(ViralGenomicAnalysisView, self).__init__(context, request)
        self.title = self.context.Title()
        self.context = context
        self.request = request

    def __call__(self):

        # samples = self.context.getSamplesList()

        workflow = getToolByName(self.context, 'portal_workflow')
        reviewState = workflow.getInfoFor(self.context, 'review_state')

        self.reviewState = reviewState
        self.absolute_url = self.context.absolute_url()
        self.id = self.context.getId()
        self.viral_genomic_analysis_uid = self.context.UID()
        self.title = self.context.Title()
        self.description = self.context.Description()
        self.project = self.get_project()
        self.date_created = self.context.getDateCreated()
        self.will_extract = self.context.getWillExtract()
        self.will_aliquot = self.context.getWillAliquot()
        self.will_quantify = self.context.getWillQuantify()
        self.will_viral_load_determine = self.context.getWillViralLoadDetermine()
        self.will_library_prep = self.context.getWillLibraryPrep()
        self.extract_genomic_material = self.prepare_extract_genomic_material()
        self.virus_aliquots = self.context.prepare_virus_aliquots()
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

    def prepare_extract_genomic_material(self):

        extract_genomic_material_rows = self.context.getExtractGenomicMaterial()
        prepared_extracts = []

        for extract in extract_genomic_material_rows:
            prepared_extract = {
                'title': extract.Title(),
                'virus_sample': self.get_virus_sample(extract),
                'heat_inactivated': extract.getField('HeatInactivated').get(extract),
                'method': self.get_method(extract),
                'extraction_barcode': extract.getField('ExtractionBarcode').get(extract),
                'volume': extract.getField('Volume').get(extract),
                'unit': extract.getField('Unit').get(extract),
                'was_kit_used': extract.getField('WasKitUsed').get(extract),
                'kit_number': extract.getField('KitNumber').get(extract),
                'notes': extract.getField('Notes').get(extract),
            }
            prepared_extracts.append(prepared_extract)

        return prepared_extracts

    # def prepare_virus_aliquots(self):
    #     virus_aliquots = self.context.getVirusAliquot()
    #     virus_aliquots_dict = {}
    #
    #     for virus_aliquot in virus_aliquots:
    #         parent_sample = self.get_parent_sample(virus_aliquot)
    #         prepared_aliquot_list = self.get_prepared_aliquots(virus_aliquot.getAliquotSample())
    #         virus_aliquots_dict[parent_sample] = prepared_aliquot_list
    #
    #     return virus_aliquots_dict
    #
    # def get_prepared_aliquots(self, aliquot_rows):
    #     prepared_aliquots = []
    #
    #     for aliquot in aliquot_rows:
    #         prepared_extract = {
    #             'barcode': aliquot.getField('Barcode').get(aliquot),
    #             'volume': aliquot.getField('Volume').get(aliquot),
    #             'unit': aliquot.getField('Unit').get(aliquot),
    #             'sample_type': self.get_sample_type(aliquot),
    #             'date_created': aliquot.getField('DateCreated').get(aliquot),
    #         }
    #         prepared_aliquots.append(prepared_extract)
    #
    #     return prepared_aliquots

    def get_project(self):
        try:
            return self.context.getProject().Title()
        except:
            return ''

    # def get_virus_sample(self, extract):
    #     try:
    #         virus_sample = extract.getField('VirusSample').get(extract)
    #         return virus_sample.Title()
    #     except:
    #         return ''
    #
    # def get_parent_sample(self, virus_aliquot):
    #     try:
    #         parent_sample = virus_aliquot.getField('ParentSample').get(virus_aliquot)
    #         return parent_sample.Title()
    #     except:
    #         return ''
    #
    # def get_sample_type(self, aliquot):
    #     try:
    #         sample_type = aliquot.getField('SampleType').get(aliquot)
    #         return sample_type.Title()
    #     except:
    #         return ''
    #
    # def get_method(self, extract):
    #     try:
    #         method = extract.getField('Method').get(extract)
    #         return method.Title()
    #     except:
    #         return ''
