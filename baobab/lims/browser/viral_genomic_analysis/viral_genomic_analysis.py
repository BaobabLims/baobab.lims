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

        workflow = getToolByName(self.context, 'portal_workflow')
        reviewState = workflow.getInfoFor(self.context, 'review_state')

        self.reviewState = reviewState
        self.absolute_url = self.context.absolute_url()
        self.id = self.context.getId()
        self.viral_genomic_analysis_uid = self.context.UID()
        self.title = self.context.Title()
        self.description = self.context.Description()
        self.date_created = self.context.getDateCreated()
        self.will_extract = self.context.getWillExtract()
        self.will_aliquot = self.context.getWillAliquot()
        self.will_quantify = self.context.getWillQuantify()
        self.will_viral_load_determine = self.context.getWillViralLoadDetermine()
        self.will_library_prep = self.context.getWillLibraryPrep()
        self.virus_aliquots = self.context.prepare_virus_aliquots()

        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

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

    # def get_project(self):
    #     try:
    #         return self.context.getProject().Title()
    #     except:
    #         return ''

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