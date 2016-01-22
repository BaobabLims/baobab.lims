# coding=utf-8

import json
import plone
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName

def getKitProducts(context, request):
    """
    KitTemplate contains a list of products
    """
    kittemplate_title = request.get('KitTemplate', '')
    catalog_name = request.get('catalog_name', '')
    catalog = getToolByName(context, catalog_name)

    brains = catalog.searchResults({'portal_type': 'KitTemplate', 'title': kittemplate_title})
    kittemplete_obj = brains[0].getObject()
    if kittemplete_obj:
        products = kittemplete_obj.getProductList()
    else:
        products = []

    return products, catalog

def getProductObject(product, catalog):
    """ get product object
    """
    brains = catalog.searchResults({'portal_type': 'Product', 'Title': product['product']})
    msg = ''
    product_obj = None
    if brains:
        if len(brains) > 1:
            msg = "Product in kit template has more than one record in Products folder!"
        else:
            product_obj = brains[0].getObject()
    else:
        msg = "Product in kit template doesn't exist!"

    return product_obj, msg

def getReferenceObjects(product_obj):
    """ Product 1..1------>0..N StockItem. Return StockItem object
    """
    msg = ''
    reference_catalog = getToolByName(product_obj, REFERENCE_CATALOG)
    references = reference_catalog.getBackReferences(product_obj, relationship="StockItemProduct")
    if not references:
        msg = "Product object has no item in the stock!"
    return references, msg

def computeRefTotalQtt(references):
    """Compute total StockItems's quantity
    """
    total_qtt = 0
    for ref in references:
        total_qtt += int(ref.getSourceObject().getQuantity())

    return total_qtt

class ComputeNumberKits():
    """
    Later please add comments
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        quantity_ratios = []
        products, catalog = getKitProducts(self.context, self.request)
        error_msg = ''
        for product in products:
            product_obj, error_msg = getProductObject(product, catalog)
            if error_msg:
                break
            references, error_msg = getReferenceObjects(product_obj)
            if error_msg:
                break
            total_qtt = computeRefTotalQtt(references)

            quantity_ratios.append(int(total_qtt / int(product['quantity'])))
        #self.context.plone_utils.addPortalMessage('Test: ' + str(min(quantity_ratios)), 'warning')
        if quantity_ratios:
            return json.dumps({'qtt':min(quantity_ratios), 'error_msg': error_msg})
        else:
            return json.dumps({'qtt':0, 'error_msg': error_msg})

def deductStockItemQuantities(references, product, no_kits):
    """Substract product quantities from stockitems
    """
    error_msg = ''
    ok_msg = ''
    total_qtt = computeRefTotalQtt(references)
    if int(total_qtt) < int(product['quantity']) * int(no_kits):
        error_msg = 'Quantity asked is higher than the existant in stock!'
    else:
        product_qtt = int(product['quantity']) * int(no_kits)
        for ref in references:
            stockitem_obj = ref.getSourceObject()
            if product_qtt == 0:
                break
            if (int(stockitem_obj.getQuantity()) / product_qtt) >= 1:
                rest = int(stockitem_obj.getQuantity()) - product_qtt
                ref.getSourceObject().setQuantity(rest)
                product_qtt = 0
            else:
                product_qtt -= int(stockitem_obj.getQuantity())
                stockitem_obj.setQuantity(0)

    if not error_msg:
        ok_msg = 'Product Quantities deducted from StockItems.'

    return ok_msg, error_msg

class UpdateStockItems():
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        products, catalog = getKitProducts(self.context, self.request)
        no_kits = self.request.get('quantity', '0')
        ok_msg = ''
        error_msg = ''
        for product in products:
            product_obj, msg = getProductObject(product, catalog)
            references, msg = getReferenceObjects(product_obj)
            ok_msg, error_msg = deductStockItemQuantities(references, product, no_kits)
            if error_msg:
                break
        return json.dumps({'ok_msg': ok_msg, 'error_msg': error_msg})
