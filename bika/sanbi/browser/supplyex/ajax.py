# coding=utf-8

import json
import plone
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName

class ComputeNumberKits():
    """
    Later please add comments
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        kittemplate_title = self.request.get('KitTemplate', '')
        catalog_name = self.request.get('catalog_name', '')
        catalog = getToolByName(self.context, catalog_name)

        brains = catalog.searchResults({'portal_type': 'KitTemplate', 'Title': kittemplate_title})
        kittemplete_obj = brains[0].getObject()
        if kittemplete_obj:
            products = kittemplete_obj.getProductList()
        else:
            products = []

        quantity_ratios = []
        for product in products:
            brains = catalog.searchResults({'portal_type': 'Product', 'Title': product['product']})
            product_obj = brains[0].getObject()
            reference_catalog = getToolByName(self.context, REFERENCE_CATALOG)
            stockitem_obj = reference_catalog.lookupObject(product['product_uid'])

            quantity_ratios.append(int(int(stockitem_obj.getQuantity()) / int(product['quantity'])))
        #self.context.plone_utils.addPortalMessage('Test: ' + str(min(quantity_ratios)), 'warning')
        if quantity_ratios:
            return json.dumps(min(quantity_ratios))
        else:
            return json.dumps(0)