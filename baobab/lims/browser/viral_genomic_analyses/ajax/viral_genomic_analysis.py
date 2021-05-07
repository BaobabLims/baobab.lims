import json
from operator import itemgetter

import plone
from baobab.lims.idserver import renameAfterCreation

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from bika.lims.browser import BrowserView
from bika.lims.utils import tmpID


class AjaxCreateViralGenomicAnalysis(BrowserView):

    def __init__(self, context, request):
        print('--------------init')
        super(AjaxCreateViralGenomicAnalysis, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.viral_genomic_analysis = []
        self.errors = []

    def __call__(self):

        try:
            if 'viral_genomic_analysis' not in self.request.form:
                raise Exception('No valid viral genomic analysis data found')

            viral_genomic_analysis_data = json.loads(self.request.form['viral_genomic_analysis'])
            viral_genomic_analysis_obj = self.create_viral_genomic_analysis_object(viral_genomic_analysis_data)

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

    def create_viral_genomic_analysis_object(self, viral_genomic_analysis_data):

        viral_genomic_analyses = self.context.viral_genomic_analyses
        obj = _createObjectByType('ViralGenomicAnalysis', viral_genomic_analyses, tmpID())
        project = self.get_content_type(viral_genomic_analysis_data['project'])

        obj.edit(
            title=viral_genomic_analysis_data['title'],
            description=viral_genomic_analysis_data['description'],
            Project=project,
            DateCreated=viral_genomic_analysis_data['date_created'],
            # WillExtract=viral_genomic_analysis_data['will_extract'],
            # WillAliquot=viral_genomic_analysis_data['will_aliquot'],
            # WillQuantify=viral_genomic_analysis_data['will_quantify'],
            # WillViralLoadDetermine=viral_genomic_analysis_data['will_viral_load_determine'],
            # WillLibraryPrep=viral_genomic_analysis_data['will_library_prep'],
        )

        obj.unmarkCreationFlag()

        renameAfterCreation(obj)
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
