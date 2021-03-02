from plone import api as ploneapi
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView


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
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

    def prepare_extract_genomic_material(self):

        extract_genomic_material_rows = self.context.getExtractGenomicMaterial()
        if not extract_genomic_material_rows:
            return {}

        prepared_extracts = []
        for extract in extract_genomic_material_rows:
            sample = ploneapi.content.get(UID=extract['VirusSample'])
            method = ploneapi.content.get(UID=extract['Method'])
            prepared_extract = {
                'title': extract['ExtractionBarcode'],
                'virus_sample': sample.Title() if sample else '',
                'heat_inactivated': extract['HeatInactivated'],
                'method': method.Title() if method else '',
                'extraction_barcode': extract['ExtractionBarcode'],
                'volume': extract['Volume'],
                'unit': extract['Unit'],
                'was_kit_used': extract['WasKitUsed'],
                'kit_number': extract['KitNumber'],
                'notes': extract['Notes'],
            }
            prepared_extracts.append(prepared_extract)

        return prepared_extracts

    def get_project(self):
        try:
            return self.context.getProject().Title()
        except:
            return ''
