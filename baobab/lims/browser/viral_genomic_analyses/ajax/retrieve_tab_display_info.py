from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView

from Products.CMFPlone.utils import _createObjectByType
from baobab.lims.idserver import renameAfterCreation

from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor

import json

class AjaxRetrieveTabDisplayInfo(BrowserView):

    def __init__(self, context, request):
        super(AjaxRetrieveTabDisplayInfo, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.viral_genomic_analysis = []
        self.errors = []

    def __call__(self):

        try:

            if 'vga_info' not in self.request.form:
                raise Exception('No valid extract genomic material data found')

            sample_aliquots_data = json.loads(self.request.form['vga_info'])
            viral_genomic_analysis_uid = sample_aliquots_data.get('viral_genomic_analysis_uid', None)

            viral_genomic_analysis_obj = self.get_content_type(viral_genomic_analysis_uid)

            tab_display_info = self.retrieve_tab_display_info(viral_genomic_analysis_obj)

        except Exception as e:
            error_message = json.dumps({'error_message': str(e)})

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(500)
            self.request.RESPONSE.write(error_message)
        else:
            output = json.dumps(
                tab_display_info
            )

            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            self.request.RESPONSE.setStatus(200)
            self.request.RESPONSE.write(output)

    def retrieve_tab_display_info(self, viral_genomic_analysis_obj):
        tab_display_info = {}

        workflow = getToolByName(self.context, 'portal_workflow')
        reviewState = workflow.getInfoFor(viral_genomic_analysis_obj, 'review_state')

        tab_display_info['vga_status'] = reviewState
        tab_display_info['vga_will_extract'] = viral_genomic_analysis_obj.getField('WillExtract').get(viral_genomic_analysis_obj)
        tab_display_info['vga_will_aliquot'] = viral_genomic_analysis_obj.getField('WillAliquot').get(viral_genomic_analysis_obj)
        tab_display_info['vga_will_quantify'] = viral_genomic_analysis_obj.getField('WillQuantify').get(viral_genomic_analysis_obj)
        tab_display_info['vga_will_viral_load_determine'] = viral_genomic_analysis_obj.getField('WillViralLoadDetermine').get(viral_genomic_analysis_obj)
        tab_display_info['vga_will_library_prep'] = viral_genomic_analysis_obj.getField('WillLibraryPrep').get(viral_genomic_analysis_obj)

        return tab_display_info

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