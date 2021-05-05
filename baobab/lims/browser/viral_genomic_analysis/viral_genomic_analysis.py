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