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

    brains = catalog.searchResults(
        {'portal_type': 'KitTemplate', 'title': kittemplate_title})
    kittemplate_obj = brains[0].getObject()

    if kittemplate_obj:
        products = kittemplate_obj.getProductList()
    else:
        products = []

    return products, catalog, kittemplate_obj


def getProductObject(product, catalog):
    """ get product object
    """
    brains = catalog.searchResults(
        {'portal_type': 'Product', 'Title': product['product']})
    msg = ''
    product_obj = None
    if brains:
        if len(brains) > 1:
            msg = "Product in kit template has more than one record in " \
                  "Products folder!"
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
    references = reference_catalog.getBackReferences(product_obj,
                                                     relationship="StockItemProduct")
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
        products, catalog, kittemplate_obj = getKitProducts(self.context,
                                                            self.request)
        error_msg = ''
        product_dict = {}
        if kittemplate_obj.kittemplate_lineitems:
            kittemplate_obj.kittemplate_lineitems = []
        for product in products:
            product_obj, error_msg = getProductObject(product, catalog)
            product_dict[product_obj.Title()] = {
                'quantity': product['quantity'] * int(
                    self.request.get('kit_quantity', 1)),
                'price': product_obj.getPrice()
            }
            kittemplate_obj.kittemplate_lineitems.append(
                {'Product': product_obj.Title(),
                 'Quantity': product.get('quantity', 0) * \
                             int(self.request.get('kit_quantity', 1)),
                 'Price': product_obj.getPrice(),
                 'VAT': product_obj.getVAT()})
            if error_msg:
                break
            references, error_msg = getReferenceObjects(product_obj)
            if error_msg:
                break
            total_qtt = computeRefTotalQtt(references)

            quantity_ratios.append(int(total_qtt / int(product['quantity'])))

        # self.context.plone_utils.addPortalMessage('Test: ' + str(min(
        # quantity_ratios)), 'warning')
        subtotal = '%.2f' % kittemplate_obj.getSubtotal()
        vat = '%.2f' % kittemplate_obj.getVATAmount()
        total = '%.2f' % kittemplate_obj.getTotal()

        if quantity_ratios:
            return json.dumps(
                {'qtt': min(quantity_ratios), 'products': product_dict,
                 'error_msg': error_msg,
                 'currency': self.context.bika_setup.getCurrency(),
                 'subtotal': subtotal,
                 'vat': vat, 'total': total})
        else:
            return json.dumps(
                {'qtt': 0, 'products': product_dict, 'error_msg': error_msg,
                 'currency': self.context.bika_setup.getCurrency(),
                 'subtotal': subtotal,
                 'vat': vat, 'total': total})


def deductStockItemQuantities(references, product, no_kits, old_no_kits):
    """Substract product quantities from stockitems
    """
    error_msg = ''
    ok_msg = ''
    total_qtt = computeRefTotalQtt(references)
    if int(total_qtt) < int(product['quantity']) * (
        int(no_kits) - int(old_no_kits)):
        error_msg = 'Quantity asked is higher than the existant in stock!'
    else:
        product_qtt = int(product['quantity']) * (
        int(no_kits) - int(old_no_kits))
        for ref in references:
            stockitem_obj = ref.getSourceObject()
            if product_qtt == 0:
                break
            if product_qtt > 0:
                if (int(stockitem_obj.getQuantity()) / product_qtt) >= 1:
                    rest = int(stockitem_obj.getQuantity()) - product_qtt
                    ref.getSourceObject().setQuantity(rest)
                    product_qtt = 0
                else:
                    product_qtt -= int(stockitem_obj.getQuantity())
                    stockitem_obj.setQuantity(0)
            else:
                rest = int(stockitem_obj.getQuantity()) - product_qtt
                stockitem_obj.setQuantity(rest)

    if not error_msg:
        ok_msg = 'Product Quantities deducted from StockItems.'

    return ok_msg, error_msg


class UpdateStockItems():
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        products, catalog, _ = getKitProducts(self.context, self.request)
        object_exists = ObjectExists(self.context, self.request)
        old_no_kits = object_exists.old_quantity()
        no_kits = self.request.get('quantity', '0')
        ok_msg = ''
        error_msg = ''
        for product in products:
            product_obj, msg = getProductObject(product, catalog)
            references, msg = getReferenceObjects(product_obj)
            ok_msg, error_msg = deductStockItemQuantities(references, product,
                                                          no_kits, old_no_kits)
            if error_msg:
                break
        return json.dumps({'ok_msg': ok_msg, 'error_msg': error_msg})


class ObjectExists():
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj_exists = self.context.aq_parent.hasObject(self.context.getId())
        return json.dumps({'exist': obj_exists})

    def old_quantity(self):
        """Get the old quantity if the object exists in the db or 0
        """
        kit_quantity = 0
        obj_exists = self.context.aq_parent.hasObject(self.context.getId())
        if obj_exists:
            kit_quantity = self.context.getQuantity()

        return kit_quantity
