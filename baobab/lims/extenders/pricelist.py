from archetypes.schemaextender.interfaces import ISchemaModifier
from zope.component import adapts
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from baobab.lims import bikaMessageFactory as _
from bika.lims.interfaces import IPricelist
from baobab.lims.config import PRICELIST_TYPES
from bika.lims.config import PROJECTNAME as BIKALIMS_PROJECTNAME
from Products.Archetypes import atapi
from bika.lims.content.pricelist import Pricelist as BasePricelist
from bika.lims.content.pricelist import PricelistLineItem


class PricelistSchemaExtender(object):
    adapts(IPricelist)
    implements(ISchemaModifier)

    fields = []

    def __init__(self, context):
        self.context = context

    # def getFields(self):
    #     return self.fields

    def fiddle(self, schema):
        schema['Type'].vocabulary = PRICELIST_TYPES

# class Pricelist(BasePricelist):
#     """ Inherits from bika.content.pricelist.Pricelist
#     """
#     pass
#
# atapi.registerType(Pricelist, BIKALIMS_PROJECTNAME)


def ObjectModifiedEventHandler(instance, event):
    """Various types need automation on edit.
    """
    if not hasattr(instance, 'portal_type'):
        return

    if instance.portal_type == 'Pricelist' and \
                    instance.getType() in ['StorageType', 'KitTemplate']:

        """ Create price list line items
        """
        storage_pricing = instance.bika_setup.StoragePricing
        storage_types = [t['storage_type'] for t in storage_pricing]
        instance.pricelist_lineitems = []

        for p in instance.bika_setup_catalog(portal_type=instance.getType(),
                                             inactive_state="active"):
            obj = p.getObject()
            itemDescription = None
            itemAccredited = False
            itemTitle = obj.Title()
            cat = None

            if instance.getType() == 'StorageType':

                if itemTitle in storage_types:
                    storage_type = filter(lambda t: t['storage_type'] == itemTitle, storage_pricing)
                    price = float(storage_type[0]['price'])
                    totalprice = price
                    vat = totalprice - price
                else:
                    price = 0
                    totalprice = 0
                    vat = 0

            elif instance.getType() == 'KitTemplate':

                if obj.getCost():
                    price = float(obj.getCost())
                    totalprice = float(obj.getPrice())
                    vat = float(obj.getVAT())
                else:
                    price = 0
                    totalprice = 0
                    vat = 0

            if instance.getDescriptions():
                itemDescription = obj.Description()

            li = PricelistLineItem()
            li['title'] = itemTitle
            li['ItemDescription'] = itemDescription
            li['CategoryTitle'] = cat
            li['Accredited'] = itemAccredited
            li['Subtotal'] = "%0.2f" % price
            li['VATAmount'] = "%0.2f" % vat
            li['Total'] = "%0.2f" % totalprice
            instance.pricelist_lineitems.append(li)
