import traceback
from zope.interface.declarations import implements
from Products.Five import BrowserView
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema import ValidationError
from DateTime import DateTime

from bika.lims.browser.invoice import InvoiceView
from bika.lims.idserver import renameAfterCreation
from baobab.lims.browser import _createdby_data, _printedby_data, _lab_data
from baobab.lims.config import INVOICE_SERVICES
from baobab.lims import bikaMessageFactory as _
import os


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

            from Products.CMFPlone.utils import _createObjectByType
            from bika.lims.utils import tmpID
            instance = _createObjectByType('InvoiceBatch', self.context, tmpID(), title=data['title'])
            instance.unmarkCreationFlag()
            instance.edit(
                Project=data['project_uid'],
                Services=data['services'],
                BatchStartDate=data['start_date'],
                BatchEndDate=data['end_date']
            )
            renameAfterCreation(instance)
            instance.processForm()
            msg = u'Invoice for period "%s" to "%s" created.' % (data['start_date'], data['end_date'])
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def validate_form_inputs(self):
        """Validate form inputs
        """
        form = self.request.form
        if not form['title']:
            raise ValidationError('Title should be specified for this invoice!')
        if not form['invoice_services']:
            raise ValidationError('Invoice service is required!')
        if form['startdate'] and form['enddate']:
            if form['enddate'] < form['startdate']:
                raise ValidationError(u"Start date, '%s', shouldn't be greater than End date, '%s'!" %(form['startdate'], form['enddate']))

        return {
            'title': form['title'],
            'project_uid': form['Project_uid'],
            'services': form['invoice_services'],
            'start_date': form['startdate'],
            'end_date': form['enddate']
        }

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())


class InvoicePrintView(InvoiceView):
    """Print invoice
    """
    template = ViewPageTemplateFile("templates/invoice_print.pt")
    _TEMPLATES_DIR = 'templates/invoice'

    def __call__(self):
        """Entry point to the class
        """
        return InvoiceView.__call__(self)
        # return self.template()

    def get_css(self):
        """Import the template accompanying css file
        """
        template_name = 'invoice.pt'
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
        path = '%s/%s.css' % (templates_dir, template_name[:-3])
        with open(path, 'r') as content_file:
            content = content_file.read()

        return content

    def render_invoice(self):
        """Render template
        """
        templates_dir = self._TEMPLATES_DIR
        template_name = 'invoice.pt'

        template_file = ViewPageTemplateFile(os.path.join(templates_dir, template_name))
        embed = template_file
        try:
            rep_template = embed(self)
        except:
            tbex = traceback.format_exc()
            ktid = self.context.id
            rep_template = "<div class='error-print'>%s - %s " \
                           "'%s':<pre>%s</pre></div>" % (
                              ktid, _("Unable to load the template"), template_name, tbex)

        return rep_template

    def get_invoice_info(self):
        data = {}
        data['date_printed'] = self.ulocalized_time(DateTime(), long_format=1)
        data['date_created'] = self.ulocalized_time(self.context.created(),
                                                    long_format=1)
        data['createdby'] = _createdby_data(self)
        data['printedby'] = _printedby_data(self)
        data['laboratory'] = _lab_data(self)

        return data
