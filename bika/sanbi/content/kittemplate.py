from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName
from bika.sanbi import config
from bika.lims.content.bikaschema import BikaSchema
from DateTime.DateTime import DateTime
from decimal import Decimal
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
import sys
from Products.ATExtensions.ateapi import RecordField, RecordsField
from bika.lims.browser.widgets.recordswidget import RecordsWidget

from Products.CMFCore.permissions import View
from bika.sanbi.interfaces import IKitTemplate

schema = BikaSchema.copy() + Schema((
    ReferenceField('Category',
        required=1,
        vocabulary='getCategories',
        allowed_types=('ProductCategory',),
        relationship='KitTemplateProductCategory',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label = _("Product Category"),
            description = _(""),
        ),
    ),
    RecordsField('ProductList',
        schemata="Product List",
        type='productList',
        subfields=('product', 'quantity', 'product_uid'),
        subfield_hidden = {'product_uid': True},
        required_subfields=('product', 'quantity', 'product_uid'),
        subfield_sizes={'product': 50, 'quantity': 5,},
        subfield_labels={'product': _('Product'),
                         'quantity': _('Quantity'),
        },
        widget=RecordsWidget(
         label = _("Product List"),
         description=_("Select complete list of the components required to create this kit"),
         combogrid_options={
                 'product': {
                     'colModel': [{'columnName':'product', 'width':'30', 'label':_('Title')},
                                  {'columnName':'Description', 'width':'70', 'label':_('Description')},
                                  {'columnName': 'product_uid', 'hidden': True}],
                     'url': 'getproducts',
                     'showOn': True,
                     'width': '550px'
                 },
         },
        ),
    ),
    IntegerField('Quantity',
        widget = IntegerWidget(
            label=_("Quantity"),
            description=_("The number of items of this product already in "
                          "storage. eg. 15, 100"),
        ),
    ),
    TextField('StorageConditions',
        default_output_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget (
            label = _("Storage Conditions")),
            description=_("Requirements for storing the product."),
    ),
    FixedPointField('Price',
        schemata='Price',
        default='0.00',
        widget = DecimalWidget(
            label=_("Price excluding VAT"),
            description=_("This is the price will be charged for each completed kit."),
        )
    ),
    FixedPointField('VAT',
        schemata='Price',
        default_method='getDefaultVAT',
        widget = DecimalWidget(
            label=_("VAT %"),
            description=_("Enter percentage value eg. 14.0"),
        ),
    ),
    FixedPointField('Cost',
        schemata='Price',
        default_method='getCost',
        widget = DecimalWidget(
            label=_("Cost"),
            size=10,
            description=_("This is the base cost of the components required for each completed kit."),
        ),
    ),
    ComputedField('VATAmount',
        expression = 'context.getVATAmount()',
        widget = ComputedWidget(
            label=_("VAT"),
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('CategoryTitle',
        expression="context.getCategory() and context.getCategory().Title() or ''",
        widget=ComputedWidget(visible=False),
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

    security.declarePublic('getCategories')
    def getCategories(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        deps = []
        for d in bsc(portal_type='ProductCategory',
                     inactive_state='active'):
            deps.append((d.UID, d.Title))
        return DisplayList(deps)

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
                [(Decimal(obj['Quantity']) * Decimal(obj['Price'])) for obj in self.kittemplate_lineitems])
        return 0

    security.declareProtected(View, 'getTotal')
    def getTotal(self):
        """Compute total price
        """
        total = 0
        for lineitem in self.kittemplate_lineitems:
            total += Decimal(lineitem['Quantity']) * \
                     Decimal(lineitem['Price']) * \
                     ((Decimal(lineitem['VAT']) /100) + 1)
        return total

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

        # TODO: Chech wich one to use here, str or decimal?
        #return price.quantize(Decimal('0.00'))
        return str(price)

    '''
    security.declarePublic('getTotalPrice')
    def getTotalPrice(self):
        """ compute total price """
        price = self.getPrice()
        price = Decimal(price or '0.00')
        vat = Decimal(self.getVAT())
        price = price and price or 0
        vat = vat and vat / 100 or 0
        price = price + (price * vat)
        return price.quantize(Decimal('0.00'))

    security.declarePublic('getVATAmount')
    def getVATAmount(self):
        """ Compute VATAmount
        """
        try:
            vatamount = self.getTotalPrice() - Decimal(self.getPrice())
        except:
            vatamount = Decimal('0.00')
        return vatamount.quantize(Decimal('0.00'))
    '''


registerType(KitTemplate, config.PROJECTNAME)
