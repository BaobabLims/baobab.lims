from Products.ATContentTypes.lib import constraintypes
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from plone import api
from plone.app.layout.viewlets import ViewletBase
from baobab.lims.browser.project import *
from baobab.lims.browser.project.util import SampleGeneration
from baobab.lims.interfaces import IUnmanagedStorage, IStoragePosition, IManagedStorage
from baobab.lims.permissions import ManageKits
from Products.CMFCore.utils import getToolByName

from bika.lims.utils import tmpID
from bika.lims.utils import to_utf8
from bika.lims.utils import encode_header
from bika.lims.utils import createPdf
from bika.lims.utils import attachPdf
from bika.lims.utils.sample import create_sample
from bika.lims.utils.samplepartition import create_samplepartition
import datetime


class DownloadVGAReport(BrowserView):

    template = ViewPageTemplateFile("templates/download_viral_genomic_analysis_report.pt")

    def __init__(self, context, request):
        super(DownloadVGAReport, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')

    def __call__(self):
        self.prepare_overhead_data()
        self.prepare_report()
        self.now = datetime.datetime.now()
        pdf_data = createPdf(htmlreport=self.template())

        date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        setheader = self.request.RESPONSE.setHeader
        setheader("Content-type", "application/pdf")
        setheader("Content-Disposition",
                  "attachment;filename=\"viral_genomic_analysis_%s.pdf\"" % date)

        self.request.RESPONSE.write(pdf_data)

    def prepare_report(self):
        self.title = self.context.Title()
        self.date_created = self.context.getDateCreated()
        self.project = self.context.getProject().Title()
        self.prepared_viral_loads = self.context.prepare_viral_load_data()

    def prepare_overhead_data(self):

        pc = self.portal_catalog
        self.checkPermission = self.context.portal_membership.checkPermission
        self.SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()

        # Client details (if client is associated)
        project = self.context.getProject()
        client = project.getClient()

        if client:
            self.client = client
            client_address = self.client.getPostalAddress()
            if not client_address:
                client_address = self.contact.getBillingAddress()
                if not client_address:
                    client_address = self.contact.getPhysicalAddress()
            if client_address:
                _keys = ['address', 'city', 'state', 'zip', 'country']
                _list = [client_address.get(v) for v in _keys if client_address.get(v)]
                self.client_address = "<br/>".join(_list).replace("\n", "<br/>")
                if self.client_address.endswith("<br/>"):
                    self.client_address = self.client_address[:-5]
            else:
                self.client_address = None

        # Reporter
        self.member = self.context.portal_membership.getAuthenticatedMember()
        self.username = self.member.getUserName()
        self.reporter = self.user_fullname(self.username)
        self.reporter_email = self.user_email(self.username)
        self.reporter_signature = ""
        c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
             if x.getObject().getUsername() == self.username]
        if c:
            sf = c[0].getObject().getSignature()
            if sf:
                self.reporter_signature = sf.absolute_url() + "/Signature"

        # laboratory
        self.laboratory = self.context.bika_setup.laboratory
        self.accredited = self.laboratory.getLaboratoryAccredited()
        lab_address = self.laboratory.getPrintAddress()

        if lab_address:
            self.lab_address = lab_address
        else:
            self.lab_address = None









