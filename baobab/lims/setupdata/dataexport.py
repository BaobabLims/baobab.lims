import collections

import os
import json

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.lims.exportimport.dataimport import ImportView as IV
from exporters import *
from excelwriter import ExcelWriter

from bika.lims.browser import BrowserView


class RemoveExports(BrowserView):
    _DOWNLOADS_DIR = 'static/downloads/'

    def __init__(self, context, request):

        super(RemoveExports, self).__init__(context, request)
        self.context = context
        self.request = request

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.download_dir = os.path.join(base_dir, self._DOWNLOADS_DIR)

    def __call__(self):
        uc = getToolByName(self.context, 'portal_catalog')

        filename = self.download_dir + self.request.form['id']
        if os.path.exists(filename):
            os.remove(filename)

        return json.dumps({
            'row_id': self.request.form['id']
        })


class ExportView(IV):
    """
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/export.pt")
    _DOWNLOADS_DIR = 'static/downloads/'

    def __init__(self, context, request):
        IV.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        if 'submitted' in self.request:
            lab = self.context.bika_setup.laboratory
            self.excel_writer = ExcelWriter(self.context)
            self.excel_writer.create_workbook()

            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            self.download_dir = os.path.join(base_dir, self._DOWNLOADS_DIR)

            self.export_data()

            self.download_file = True
            self.files = self.get_filenames()
            self.context.plone_utils.addPortalMessage(
                'Export successfully completed.')
        else:
            self.submit_button = True
        return self.template()

    def get_filenames(self):
        from os import listdir
        from os.path import isfile, join, getmtime

        files = [f for f in listdir(self.download_dir) if isfile(
            join(self.download_dir, f))]

        files.sort(key=lambda x: getmtime(
            join(self.download_dir, x)), reverse=True)
        return files

    def export_data(self):
        export_dict = collections.OrderedDict()

        exporter = ProjectsExporter(self.context)
        export_dict['Projects'] = exporter.export()

        # exporter = SamplesExporter(self.context)
        # export_dict['Parent Samples'] = exporter.export()

        exporter = SamplesExporter(self.context)
        export_dict['Samples'] = exporter.export()

        exporter = VirusSamplesExporter(self.context)
        export_dict['VirusSamples'] = exporter.export()

        exporter = SampleShipmentExporter(self.context)
        export_dict['Sample Shipment'] = exporter.export()

        exporter = ViralGenomicAnalysisExporter(self.context)
        export_dict['Viral Genomic Analysis'] = exporter.export()

        exporter = ExtractGenomicMaterialExporter(self.context)
        export_dict['Extract Genomic Material'] = exporter.export()

        exporter = GenomeQuantificationExporter(self.context)
        export_dict['Genome Quantification'] = exporter.export()

        exporter = ViralLoadDeterminationExporter(self.context)
        export_dict['Viral Load Determination'] = exporter.export()

        exporter = SequenceLibraryPrepExporter(self.context)
        export_dict['Sequence Library Prep'] = exporter.export()

        self.excel_writer.write_output(export_dict)