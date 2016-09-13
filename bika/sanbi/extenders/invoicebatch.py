from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from zope.interface import implements
from zope.component import adapts
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.atapi import SelectionWidget
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.CMFPlone.utils import _createObjectByType
from zope.container.contained import ContainerModifiedEvent

from bika.lims.content.invoice import InvoiceLineItem
from bika.lims.fields import ExtReferenceField, ExtStringField
from bika.lims.interfaces import IInvoiceBatch
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.config import ManageInvoices
from bika.lims.content.invoicebatch import InvoiceBatch
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.config import INVOICE_SERVICES


class InvoiceBatchSchemaExtender(object):
    adapts(IInvoiceBatch)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField(
            'Project',
            allowed_types=('Project',),
            relationship='InvoiceProject',
            referenceClass=HoldingReference,
            widget=bika_ReferenceWidget(
                label=_("Project"),
                catalog_name='bika_catalog',
                size=30,
                showOn=True,
                description=_("Click and select project for the kit."),
            )
        ),
        ExtStringField(
            'Service',
            searchable=True,
            vocabulary=INVOICE_SERVICES,
            widget=SelectionWidget(
                format="select",
                label=_("Service"),
                description=_("Select the service to invoice."),
            )
        )
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        sch = schematas['default']
        sch.remove('Project')
        sch.remove('Service')
        sch.insert(sch.index('BatchStartDate'), 'Project')
        sch.insert(sch.index('BatchStartDate'), 'Service')
        schematas['default'] = sch
        return schematas


class Invoicing(InvoiceBatch):
    """Class for creating invoices.
    """

    security = ClassSecurityInfo()

    def __init__(self, instance, project, service, brains):
        super(Invoicing, self).__init__(self)
        self.instance = instance
        self.project = project
        self.service = service
        self.brains = brains
        self.client_uid = self.project.getClient().UID()

    security.declareProtected(ManageInvoices, 'create_invoice')

    def create_invoice(self):
        invoice_id = self.instance.generateUniqueId('Invoice')
        invoice = _createObjectByType("Invoice", self.instance, invoice_id)
        invoice.edit(
            Client=self.client_uid,
            InvoiceDate=DateTime(),
        )
        invoice.processForm()
        invoice.invoice_lineitems = []
        start = self.instance.getBatchStartDate()
        end = self.instance.getBatchEndDate()
        if self.service == 'Kit':
            sub_total, vat = 0, 0
            for brain in self.brains:
                kit = brain.getObject()
                kit_template = kit.getKitTemplate()
                sub_total += float(kit_template.getPrice())
                vat = float(kit_template.getVAT())
            total = sub_total + (sub_total * vat / 100)

            lineitem = InvoiceLineItem()
            lineitem['ItemDate'] = self.project.getDateCreated()
            lineitem['OrderNumber'] = self.project.getId()
            lineitem['AnalysisRequest'] = ''
            lineitem['SupplyOrder'] = ''
            lineitem['Project'] = self.project
            lineitem['ItemDescription'] = 'Kit invoicing for the period {} to {}'.format(start.strftime('%Y-%m-%d'),
                                                                                         end.strftime('%Y-%m-%d'))
            lineitem['Subtotal'] = sub_total
            lineitem['VATAmount'] = vat
            lineitem['Total'] = total
            invoice.invoice_lineitems.append(lineitem)
        invoice.reindexObject()
        return invoice

def ObjectModifiedEventHandler(instance, event):
    """Create kit and storage invoices
    """
    if not isinstance(event, ContainerModifiedEvent):
        start = instance.getBatchStartDate()
        end = instance.getBatchEndDate()
        field = instance.getField('Service')
        service = field.getAccessor(instance)()
        field = instance.getField('Project')
        project = field.getAccessor(instance)()

        # field.getMutator(instance)('Storage')

        # Query for kits in date range
        brains = []
        if service == 'Kit':
            query = {
                'portal_type': 'Kit',
                'inactive_state': 'active',
                'kit_project_uid': project.UID(),
                'getDateCreated': {
                    'range': 'min:max',
                    'query': [start, end]
                }
            }

            brains = instance.bika_catalog(query)

        invoicing = Invoicing(instance, project, service, brains)
        invoicing.create_invoice()
