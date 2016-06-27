from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName
from bika.sanbi import config
from bika.lims.content.bikaschema import BikaSchema
from decimal import Decimal
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import RecordField, RecordsField
from bika.lims.browser.widgets.recordswidget import RecordsWidget
from Products.Archetypes.references import HoldingReference

from Products.CMFCore.permissions import View
from bika.sanbi.interfaces import IKitTemplate

schema = BikaSchema.copy() + Schema((
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
    FixedPointField('Price',
        schemata='Price',
        default= "0.0",
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
        default_method='getTotal',
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
    ReferenceField('Category',
        required=1,
        vocabulary='get_kit_category',
        allowed_types=('ProductCategory',),
        relationship='KitCategory',
        widget=SelectionWidget(
           format='select',
           label=_("Product Category"),
           description=_(""),
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

    security.declarePublic('get_kit_category')
    def get_kit_category(self):
        catalog = getToolByName(self, 'bika_setup_catalog')
        categories = []
        brains = catalog.searchResults(portal_type="ProductCategory")
        for brain in brains:
            categories.append([brain.UID, brain.title])
        categories.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return DisplayList(categories)

registerType(KitTemplate, config.PROJECTNAME)
