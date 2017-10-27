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

import plone


class ImportView(IV):
    """
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/import.pt")

    def __init__(self, context, request):
        IV.__init__(self, context, request)
        self.context = context
        self.request = request

    def import_form(self):
        """This is a trick to allow non-robot tests to access the import form
        without javascript.
        """
        exim = self.request.get('exim')
        if exim:
            exim = exim.replace(".", "/")
            import os.path
            instrpath = os.path.join("exportimport", "instruments")
            templates_dir = resource_filename("bika.lims", instrpath)
            fname = "%s/%s_import.pt" % (templates_dir, exim)
            return ViewPageTemplateFile("instruments/%s_import.pt" % exim)(self)
        else:
            return ""

    def getSetupDatas(self):
        datasets = []
        adapters = getAdapters((self.context, ), ISetupDataSetList)
        for name, adapter in adapters:
            if name == 'baobab.lims':
                datasets.extend(adapter())
        return datasets

    def __call__(self):
        if 'submitted' in self.request:
            if 'setupfile' in self.request.form or \
                            'setupexisting' in self.request.form:
                lsd = LoadSetupData(self.context, self.request)
                return lsd()
            else:
                exim = instruments.getExim(self.request['exim'])
                return exim.Import(self.context, self.request)
        else:
            return self.template()

    def getDataInterfaces(self, export_only=False):
        exims = []
        for exim_id in instruments.__all__:
            exim = instruments.getExim(exim_id)
            if export_only and not hasattr(exim, 'Export'):
                pass
            else:
                exims.append((exim_id, exim.title))
        exims.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        exims.insert(0, ('', t(_('None'))))
        return DisplayList(exims)

class ajaxGetImportTemplate(IV):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        exim = self.request.get('exim').replace(".", "/")
        import os.path
        if exim == 'biorad/tc20/tc20':
            dirname = "setupdata"
            prjname = "baobab.lims"
        else:
            dirname = "exportimport"
            prjname = "bika.lims"

        instrpath = os.path.join(dirname, "instruments")
        templates_dir = resource_filename(prjname, instrpath)
        fname = "%s/%s_import.pt" % (templates_dir, exim)

        if os.path.isfile(fname):
            return ViewPageTemplateFile(fname)(self)
        else:
            # use bika lims default template
            dname = "%s/instrument.pt" % resource_filename("bika.lims", os.path.join("exportimport", "instruments"))
            return ViewPageTemplateFile(dname)(self)
