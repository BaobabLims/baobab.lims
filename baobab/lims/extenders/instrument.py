from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from zope.component import adapts

from bika.lims.fields import *
from bika.lims.interfaces import IInstrument

from baobab.lims import bikaMessageFactory as _


class InstrumentSchemaExtender(object):
    adapts(IInstrument)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField(
            'Manufacturer',
            vocabulary='getManufacturers',
            allowed_types=('Manufacturer',),
            relationship='InstrumentManufacturer',
            required=0,
            widget=SelectionWidget(
                format='select',
                label=_("Manufacturer"),
                visible={'view': 'invisible', 'edit': 'invisible'}
            ),
        )
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        return schematas
