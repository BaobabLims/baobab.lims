from zope.interface.declarations import implements
from Products.Five import BrowserView
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema import ValidationError
from plone import api

from bika.lims.idserver import renameAfterCreation
from bika.sanbi.config import INVOICE_SERVICES


class AddInvoiceViewlet(ViewletBase):
    """Viewlet form below content title to add invoices.
    """
    index = ViewPageTemplateFile("add_invoice_viewlet.pt")

    invoice_services = INVOICE_SERVICES.items()
    # print invoice_services.items()

    def render(self):
        return self.index()

class AddInvoiceSubmitHandler(BrowserView):
    """Handle submit information from invoice viewlet
    """

    def __call__(self):

        if "viewlet_submitted" in self.request.form:
            data = {}
            try:
                data = self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)
                return

            obj = api.content.create(
                container=self.context,
                title=data['title'],
                type='InvoiceBatch',
                Project=data['project_uid'],
                Service=data['service'],
                BatchStartDate=data['start_date'],
                BatchEndDate=data['end_date']
            )
            renameAfterCreation(obj)
            obj.reindexObject()

            msg = u'Invoice for period "%s" to "%s" created.' % (data['start_date'], data['end_date'])
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def validate_form_inputs(self):
        """Validate form inputs
        """
        form = self.request.form
        if not form['invoicetitle']:
            raise ValidationError('Title should be specified for this invoice!')
        if not form['invoice_service']:
            raise ValidationError('Invoice service is required!')
        if form['startdate'] and form['enddate']:
            if form['enddate'] < form['startdate']:
                raise ValidationError(u"Start date, '%s', shouldn't be greater than End date, '%s'!" %(form['startdate'], form['enddate']))

        return {
            'title': form['invoicetitle'],
            'project_uid': form['Project_uid'],
            'service': form['invoice_service'],
            'start_date': form['startdate'],
            'end_date': form['enddate']
        }

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())