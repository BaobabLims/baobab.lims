from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName
from baobab.lims import config
from bika.lims.content.bikaschema import BikaSchema
from decimal import Decimal
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import RecordField, RecordsField
from bika.lims.browser.widgets.recordswidget import RecordsWidget
from Products.Archetypes.references import HoldingReference

from Products.CMFCore.permissions import View
from baobab.lims.interfaces import IKitTemplate

schema = BikaSchema.copy() + Schema((
    RecordsField(
        'ProductList',
        schemata='Product List',
        type='productList',
        subfields=('product', 'quantity', 'product_uid'),
        subfield_hidden={'product_uid': True},
        required_subfields=('product', 'quantity', 'product_uid'),
        subfield_sizes={'product': 50, 'quantity': 5},
        subfield_labels={'product': _('Product'),
                         'quantity': _('Quantity')},
        widget=RecordsWidget(
            label=_("Product List"),
            description=_("Select complete list of the components required to create this kit."),
            combogrid_options={
                 'product': {
                     'colModel': [{'columnName': 'product', 'width': '30', 'label': _('Title')},
                                  {'columnName': 'Description', 'width': '70', 'label': _('Description')},
                                  {'columnName': 'product_uid', 'hidden': True}],
                     'url': 'getproducts',
                     'showOn': True,
                     'width': '550px'
                 },
            },
        ),
    ),
    FixedPointField(
        'Cost',
        schemata='Accounting',
        widget=DecimalWidget(
            label=_("Cost"),
            size=10,
            description=_("This is the base cost of the components required for each completed kit."),
        ),
    ),
    FixedPointField(
        'Discount',
        schemata='Accounting',
        default='0.00',
        widget=DecimalWidget(
            label=_("Discount %"),
            description=_("Enter percentage discount value eg. 2.0"),
        )
    ),
    FixedPointField(
        'VAT',
        schemata='Accounting',
        default_method='getDefaultVAT',
        widget=DecimalWidget(
            label=_("VAT %"),
            description=_("Enter percentage value eg. 14.0"),
        )
    ),
    FixedPointField(
        'DeliveryFee',
        schemata='Accounting',
        default='0.00',
        widget=DecimalWidget(
            label=_("Delivery Fee"),
            description=_("The delivery cost per kit."),
        )
    ),
    ComputedField(
        'Price',
        schemata='Price',
        expression='context.getTotal()',
        widget=DecimalWidget(
            label=_("Price excluding VAT"),
            description=_("This is the price will be charged for each completed kit. "
                          "The price will be set automatically"),
        )
    ),
    ComputedField('VATAmount',
        expression='context.getVATAmount()',
        widget=ComputedWidget(
            label=_("VAT"),
            visible={'edit': 'hidden', }
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class KitTemplate(BaseContent):
    security = ClassSecurityInfo()
    implements(IKitTemplate)
    schema = schema
    kittemplate_lineitems = []

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('kit_template_components')
    def kit_template_components(self):
        products = self.getProductList()

    security.declarePublic('getDefaultVAT')
    def getDefaultVAT(self):
        """ return default VAT from bika_setup """
        try:
            vat = self.bika_setup.getVAT()
            return vat
        except ValueError:
            return "0.00"

    security.declareProtected(View, 'getSubtotal')
    def getSubtotal(self):
        """ Compute Subtotal
        """
        if self.kittemplate_lineitems:
            return sum(
                [(Decimal(obj['quantity']) * Decimal(obj['price'])) for obj in self.kittemplate_lineitems])
        return 0

    security.declareProtected(View, '_compute_cost')
    def _compute_cost(self):
        """Return dictionary product with price
        """
        product_list = self.getProductList()
        uc = getToolByName(self, 'uid_catalog')
        cost = 0
        for p in product_list:
            brains = uc(UID=p['product_uid'])
            if brains:
                product = brains[0].getObject()
                cost += Decimal(product.getPrice()) * Decimal(p['quantity'])

        return cost

    security.declareProtected(View, 'getTotal')
    def getTotal(self):
        """Compute total price
        """
        field = self.bika_setup.getField('LevyAmount')
        cost = self._compute_cost()
        delivery = Decimal(self.getDeliveryFee())
        discount = cost * Decimal(self.getDiscount()) / 100
        levy = cost * Decimal(field.getAccessor(self.bika_setup)()) / 100
        vat = Decimal(self.getVAT())
        total = cost - discount + delivery + levy
        total *= vat / 100 + 1

        return str(total)

    security.declareProtected(View, 'getVATAmount')
    def getVATAmount(self):
        """Compute VAT
        """
        return Decimal(self.getTotal()) - Decimal(self.getSubtotal())

    security.declarePublic('getSupplierTitle')
    def getSupplierTitle(self):
        return self.aq_parent.Title()

    security.declarePublic('getCost')
    def getCost(self):
        price = Decimal("0.0")
        catalog = getToolByName(self, 'bika_setup_catalog')
        products = self.getProductList()
        for product in products:
            brains = catalog.searchResults({'portal_type': 'Product', 'title': product['product']})
            quantity = Decimal(product['quantity'])
            product_totalprice = brains[0].getObject().getTotalPrice() * quantity
            price += product_totalprice

        # TODO: Wich one to use here, str or decimal?
        #return price.quantize(Decimal('0.00'))
        return str(price)

    security.declarePublic('kit_components')
    def kit_components(self):
        """Extract information of products in kit template. These information are in kit_view.pt
        """
        catalog = getToolByName(self, 'uid_catalog')
        product_refs = self.getProductList()
        self.kittemplate_lineitems = []
        for product_ref in product_refs:
            brains = catalog(portal_type='Product', UID=product_ref['product_uid'])
            product = brains[0].getObject()
            self.kittemplate_lineitems.append({
                'title': product.Title(),
                'price': product.getPrice(),
                'VAT': product.getVAT(),
                'Discount': self.getDiscount(),
                'DeliveryFee': self.getDeliveryFee(),
                'quantity': product_ref['quantity'],
                'total_price': '%.2f' % (float(product.getPrice()) * float(product_ref['quantity']))
            })

        return self.kittemplate_lineitems

registerType(KitTemplate, config.PROJECTNAME)
