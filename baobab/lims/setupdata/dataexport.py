from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.public import DisplayList
from zope.interface import implements
from zope.component import getAdapters
from pkg_resources import *
from bika.lims import bikaMessageFactory as _
from bika.lims.exportimport.load_setup_data import LoadSetupData
from bika.lims.exportimport.dataimport import ImportView as IV
from bika.lims.utils import t
from bika.lims.interfaces import ISetupDataSetList
from baobab.lims.setupdata import instruments
import xlsxwriter
from Products.CMFCore.utils import getToolByName
from exporters import *
from excelwriter import ExcelWriter

import plone


class ExportView(IV):
    """
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/export.pt")

    def __init__(self, context, request):
        IV.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        if 'submitted' in self.request:

            # Good example of lab data is found in baobab/lims/browser/__init__.py
            lab = self.context.bika_setup.laboratory
            # print('======This is the lab===========')
            # print(lab.__dict__)


            # try:
            export_data = self.export_data()

            excel_writer = ExcelWriter()
            excel_writer.write_output(export_data)

            self.download_file = True
            self.context.plone_utils.addPortalMessage('Export successfully completed.')

            # except Exception as e:
            #     self.submit_button = True
            #     self.context.plone_utils.addPortalMessage(str(e), 'error')
        else:
            self.submit_button = True

        return self.template()

    def export_data(self):

        export_data = {}

        # # get the lab
        # lab_data_exporter = LabDataExporter(self.context)
        # lab_data_headings, lab_data = lab_data_exporter.export()
        # export_data['LabData'] = (lab_data_headings, lab_data)
        #
        # # get the lab contacts
        # lab_contacts_exporter = LabContactsExporter(self.context)
        # lab_contacts_headings, lab_contacts_data = lab_contacts_exporter.export()
        # export_data['LabContacs'] = (lab_contacts_headings, lab_contacts_data)
        #
        # # get the analysis categories
        # analysis_categories_exporter = AnalysisCategoriesExporter(self.context)
        # analysis_categories_headings, analysis_categories_data = analysis_categories_exporter.export()
        # export_data['Analysis Categories'] = (analysis_categories_headings, analysis_categories_data)
        #
        # # get the services specifications
        # analysis_services_exporter = AnalysisServicesExporter(self.context)
        # analysis_services_headings, analysis_specifications_data = analysis_services_exporter.export()
        # export_data['Analysis Services'] = (analysis_services_headings, analysis_specifications_data)
        #
        # # get the sample types
        # sample_type_exporter = SampleTypesExporter(self.context)
        # sample_type_headings, sample_type_data = sample_type_exporter.export()
        # export_data['SampleTypes'] = (sample_type_headings, sample_type_data)
        #
        # # get the clients
        # client_exporter = ClientsExporter(self.context)
        # client_headings, client_data = client_exporter.export()
        # export_data['Clients'] = (client_headings, client_data)
        #
        # # get the projects
        # project_exporter = ProjectsExporter(self.context)
        # project_headings, project_data = project_exporter.export()
        # export_data['Projects'] = (project_headings, project_data)

        # get the batch samples
        batch_sample_exporter = SampleBatchesExporter(self.context)
        batch_sample_headings, batch_sample_data = batch_sample_exporter.export()
        export_data['Batch Samples'] = (batch_sample_headings, batch_sample_data)

        # # get the samples
        # sample_exporter = SamplesExporter(self.context)
        # sample_headings, sample_data = sample_exporter.export()
        # export_data['Biospecimens'] = (sample_headings, sample_data)

        return export_data





