from zope.interface.declarations import implements
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.sanbi.config import INVOICE_SERVICES


class AddInvoiceViewlet(ViewletBase):
    """Viewlet form below content title to add invoices.
    """
    index = ViewPageTemplateFile("add_invoice_viewlet.pt")

    invoice_services = INVOICE_SERVICES.items()
    # print invoice_services.items()

    def render(self):
        return self.index()