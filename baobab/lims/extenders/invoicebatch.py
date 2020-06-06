from Products.CMFCore.utils import getToolByName
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from zope.interface import implements
from zope.component import adapts
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.atapi import SelectionWidget, MultiSelectionWidget
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.CMFPlone.utils import _createObjectByType
from zope.container.contained import ContainerModifiedEvent

from bika.lims.utils import get_invoice_item_description
from bika.lims.content.invoice import InvoiceLineItem
from bika.lims.fields import ExtReferenceField, ExtStringField, ExtLinesField
from bika.lims.interfaces import IInvoiceBatch
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.config import ManageInvoices
from bika.lims.content.invoicebatch import InvoiceBatch
from baobab.lims import bikaMessageFactory as _
from baobab.lims.config import INVOICE_SERVICES


class InvoiceBatchSchemaExtender(object):
    adapts(IInvoiceBatch)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField(
            'Project',
            allowed_types=('Project',),
            required=True,
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
        ),
        ExtLinesField(
            'Services',
            vocabulary=INVOICE_SERVICES,
            widget=MultiSelectionWidget(
                label=_("Invoice Services"),
                description=_("Select the services to invoice."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        sch = schematas['default']
        sch.remove('Project')
        sch.remove('Services')
        sch.insert(sch.index('BatchStartDate'), 'Project')
        sch.insert(sch.index('BatchStartDate'), 'Services')
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
        self.client_uid = ''
        if self.project:
            uc = getToolByName(instance, 'uid_catalog')
            p = uc(UID=self.project.UID())
            self.client_uid = p[0].getObject().aq_parent.UID()

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
        sub_total, vat, total = 0, 0, 0
        if self.service == 'Kit':
            for brain in self.brains:
                kit = brain.getObject()
                kit_template = kit.getKitTemplate()
                sub_total = float(kit_template.getSubtotal())
                vat = float(kit_template.getVATAmount())
                total = float(kit_template.getTotal())
            sub_total *= len(self.brains)
            total *= len(self.brains)
            message = 'Kit invoicing for the period {} to {}'
            line_item = self._create_lineitem(self.project, self.service, message, start, end,
                                              sub_total, vat, total)
            invoice.invoice_lineitems.append(line_item)

        elif self.service == 'Storage':
            field = self.instance.bika_setup.getField('StoragePricing')
            storage_pricing = self._pricing_dict_format(field.getAccessor(self.instance.bika_setup)())
            if not storage_pricing: return
            for brain in self.brains:
                sample = brain.getObject()
                field = sample.getField('DateCreated')
                days = int(end - field.get(sample))
                storage_location = sample.getStorageLocation()
                if storage_location and storage_location.portal_type == 'StoragePosition':
                    id = storage_location.getHierarchy().split('.')[0]
                    hierarchy = storage_location.getHierarchy().split('.')
                    for i in xrange(len(hierarchy)-2, -1, -1):
                        unit_brains = self.instance.portal_catalog(portal_type='StorageUnit', id=hierarchy[i])
                        if unit_brains:
                            storage_type = unit_brains[0].getObject().getUnitType()
                            if storage_type:
                                sub_total += float(storage_pricing[storage_type.UID()]) * days
                                break
                    else:
                        continue
            vat = float(self.instance.bika_setup.getVAT())
            total = sub_total + (sub_total * vat / 100)
            message = 'Sample storage invoicing for the period {} to {}'
            line_item = self._create_lineitem(self.project, self.service, message, start, end,
                                              sub_total, vat, total)
            invoice.invoice_lineitems.append(line_item)

        elif self.service == 'LabProduct':
            # for client_uid, orders in self.brains.items():
            for order in self.brains:
                sub_total = order.getSubtotal()
                vat = order.getVATAmount()
                total = order.getTotal()
                line_item = self._create_lineitem(order, self.service, sub_total=sub_total,
                                                  vat=vat, total=total)
                invoice.invoice_lineitems.append(line_item)

        elif self.service == 'AnalysisRequest':
            for brain in self.brains:
                ar = brain.getObject()
                sub_total = ar.getSubtotal()
                vat = ar.getVATAmount()
                total = ar.getTotal()
                line_item = self._create_lineitem(ar, self.service, sub_total=sub_total,
                                                  vat=vat, total=total)
                invoice.invoice_lineitems.append(line_item)
        invoice.reindexObject()
        return invoice

    security.declareProtected(ManageInvoices, '_create_lineitem')

    @staticmethod
    def _create_lineitem(obj, service, message='', start='', end='', sub_total=0.0, vat=0.0, total=0.0):
        lineitem = InvoiceLineItem()
        if service in ('Kit', 'Storage'):
            lineitem['ItemDate'] = start
            lineitem['OrderNumber'] = obj.getId()
            lineitem['AnalysisRequest'] = ''
            lineitem['SupplyOrder'] = ''
            lineitem['Project'] = obj
            lineitem['ItemDescription'] = message.format(start.strftime('%Y-%m-%d'),
                                                         end.strftime('%Y-%m-%d'))
        elif service == 'LabProduct':
            lineitem['ItemDate'] = obj.getDateDispatched()
            lineitem['OrderNumber'] = obj.getOrderNumber()
            lineitem['AnalysisRequest'] = ''
            lineitem['SupplyOrder'] = obj
            description = get_invoice_item_description(obj)
            lineitem['ItemDescription'] = description

        elif service == 'AnalysisRequest':
            lineitem['ItemDate'] = obj.getDatePublished()
            lineitem['OrderNumber'] = obj.getRequestID()
            lineitem['AnalysisRequest'] = obj
            lineitem['SupplyOrder'] = ''
            description = get_invoice_item_description(obj)
            lineitem['ItemDescription'] = description

        lineitem['Subtotal'] = sub_total
        lineitem['VATAmount'] = vat
        lineitem['Total'] = total

        return lineitem

    security.declareProtected(ManageInvoices, '_pricing_dict_format')

    @staticmethod
    def _pricing_dict_format(pricing_list):
        """From the list of dicts containing the pricing objects, return a simple
           dict with uid as key and price as value.
        """
        ret = {}
        for d in pricing_list:
            ret[d['storage_type_uid']] = d['price']

        return ret

def ObjectModifiedEventHandler(instance, event):
    """Create kit and storage invoices
    """
    if not isinstance(event, ContainerModifiedEvent):
        start = instance.getBatchStartDate()
        end = instance.getBatchEndDate()
        field = instance.getField('Services')
        # services = field.getAccessor(instance)()

        services = instance.Schema()['Services'].get(instance)
        field = instance.getField('Project')
        project = field.getAccessor(instance)()
        if project is None:
            # Invoice created from the analysisrequest view
            # Project is 2 parents up
            project = instance.aq_parent.aq_parent

        client = project.aq_parent
        # field.getMutator(instance)('Storage')

        # Query for kits in date range
        for service in services:
            if service == 'Kit':
                query = {
                    'portal_type': 'Kit',
                    'inactive_state': 'active',
                    'kit_project_uid': project.UID()
                }
                kit_brains = instance.bika_catalog(query)
                brains = [b for b in kit_brains if start < b.getObject().getDateCreated() < end]
                invoicing = Invoicing(instance, project, service, brains)
                invoicing.create_invoice()
            elif service == 'Storage':
                bio_query = {
                    'portal_type': 'Sample',
                    'cancellation_state': 'active',
                    'path': {'query': '/'.join(project.getPhysicalPath()), 'depth': 1}
                }
                items = instance.bika_catalog(bio_query)
                #brains = [b for b in brains if b.getObject().getDateCreated() < end]
                brains = []
                for item in items:
                    obj = item.getObject()
                    field = obj.getField('DateCreated')
                    date_created = field.get(obj)
                    if date_created < end:
                        brains.append(item)
                invoicing = Invoicing(instance, project, service, brains)
                invoicing.create_invoice()

            elif service == 'LabProduct':
                # Query for Orders in date range
                query = {
                    'portal_type': 'SupplyOrder',
                    'review_state': 'dispatched',
                    'getDateDispatched': {
                        'range': 'min:max',
                        'query': [start, end]
                    }
                }
                orders = instance.portal_catalog(query)
                clients = {}
                for p in orders:
                    obj = p.getObject()
                    if obj.getInvoiced():
                        continue
                    client_uid = obj.aq_parent.UID()
                    l = clients.get(client_uid, [])
                    l.append(obj)
                    clients[client_uid] = l

                for client_uid, lab_products in clients.items():
                    brains = lab_products
                    if project.getClient().UID() == client_uid:
                        invoicing = Invoicing(instance, project, service, brains)
                        invoicing.create_invoice()

            elif service == 'AnalysisRequest':
                query = {
                    'portal_type': 'AnalysisRequest',
                    'review_state': 'published',
                    'getInvoiceExclude': False,
                    'path': {'query': '/'.join(client.getPhysicalPath()), 'depth': 1}
                }
                items = instance.bika_catalog(query)
                brains = []
                for item in items:
                    date_published = item.getObject().getDatePublished()
                    if isinstance(date_published, unicode):
                        if isinstance(start, DateTime):
                            start =  start.strftime('%Y-%m-%d %H:%M %p')
                        if isinstance(end, DateTime):
                            end =  end.strftime('%Y-%m-%d %H:%M %p')
                    if start <= date_published <= end:
                        brains.append(item)
                invoicing = Invoicing(instance, project, service, brains)
                invoicing.create_invoice()
