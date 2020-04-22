from AccessControl import ClassSecurityInfo
from zope.interface import implements
from plone.app.folder.folder import ATFolder
from Products.ATContentTypes.content import schemata
from baobab.lims import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName
from baobab.lims.interfaces import IProduct
from baobab.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema, BikaFolderSchema
from decimal import Decimal
from Products.Archetypes.public import *
from baobab.lims.browser.widgets import ProductSuppliersWidget

schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((

    ComputedField(
        'SupplierUID',
        expression='context.aq_parent.portal_type=="Supplier" and context.aq_parent.UID() or ""',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    StringField(
        'CAS',
        searchable=True,
        widget=StringWidget(
            label=_("CAS Registry Number"),
        ),
    ),
    StringField(
        'SupplierCatalogueID',
        searchable=True,
        widget=StringWidget(
            label=_("Supplier Catalogue ID"),
        ),
    ),
    BooleanField(
        'Hazardous',
        default=False,
        widget=BooleanWidget(
            label=_("Hazardous"),
            description=_("Samples of this type should be treated as hazardous."),
        ),
    ),
    IntegerField(
        'Quantity',
        widget=IntegerWidget(
            label=_("Quantity"),
            description=_("The number of items of this product already in "
                          "storage. eg. 15, 100."),
        ),
    ),
    StringField(
        'Unit',
        widget=StringWidget(
            label=_("Unit"),
            description=_(" Unit for the quantity eg. ml or kg."),
        ),
    ),
    FixedPointField(
        'VAT',
        schemata='Price',
        default_method='getDefaultVAT',
        widget=DecimalWidget(
            label=_("VAT %"),
            description=_("Enter percentage value eg. 14.0."),
        ),
    ),
    FixedPointField(
        'Price',
        schemata='Price',
        default='0.00',
        widget=DecimalWidget(
            label=_("Price excluding VAT"),
        )
    ),
    ComputedField(
        'VATAmount',
        expression='context.getVATAmount()',
        widget=ComputedWidget(
            label=_("VAT"),
            default='14.00',
            visible={'edit': 'hidden'}
        ),
    ),
    ComputedField(
        'TotalPrice',
        expression='context.getTotalPrice()',
        widget=ComputedWidget(
            label=_("Total price"),
            visible={'edit': 'hidden', }
        ),
    ),

    ReferenceField(
        'Supplier',
        required=1,
        multiValued=1,
        allowed_types=('Supplier',),
        relationship='ProductSuppliers',
        widget=ProductSuppliersWidget(
           label=_("Suppliers"),
           description="",
        )),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class Product(ATFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    implements(IProduct)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getSuppliers(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.getName) \
                 for c in bsc(portal_type='Supplier',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def getTotalPrice(self):
        """ compute total price """
        price = self.getPrice()
        price = Decimal(price or '0.00')
        vat = Decimal(self.getVAT())
        price = price and price or 0
        vat = vat and vat / 100 or 0
        price = price + (price * vat)
        return price.quantize(Decimal('0.00'))

    def getDefaultVAT(self):
        """ return default VAT from bika_setup """
        try:
            vat = self.bika_setup.getVAT()
            return vat
        except ValueError:
            return "0.00"

    security.declarePublic('getVATAmount')
    def getVATAmount(self):
        """ Compute VATAmount
        """
        try:
            vatamount = self.getTotalPrice() - Decimal(self.getPrice())
        except:
            vatamount = Decimal('0.00')
        return vatamount.quantize(Decimal('0.00'))

    def getSupplierTitle(self):
        return self.aq_parent.Title()

    def getDocuments(self):
        """Return all the multifile objects related with the product
        """
        return self.objectValues('Multifile')

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
registerType(Product, PROJECTNAME)
