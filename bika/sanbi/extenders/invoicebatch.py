from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from zope.interface import implements
from zope.component import adapts
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.atapi import SelectionWidget

from bika.lims.fields import ExtReferenceField, ExtStringField
from bika.lims.interfaces import IInvoiceBatch
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
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