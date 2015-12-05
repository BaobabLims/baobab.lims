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
from bika.sanbi.interfaces import IKitTemplate

schema = BikaSchema.copy() + Schema((
    ReferenceField('Category',
        required=1,
        vocabulary='getCategories',
        allowed_types=('ProductCategory',),
        relationship='ProductCategory',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label = _("Product Category"),
            description = _(""),
        ),
    ),
    RecordsField('ProductList',
                 schemata="ProductList",
                 type='productList',
                 subfields=('product', 'quantiy'),
                 required_subfields=(
                 'product', 'quantity'),
                 subfield_sizes={'product': 50,
                                 'quantiy': 5,
                 },
                 subfield_labels={'product': _('Range min'),
                                  'quantiy': _('Range max'),
                 },
                 subfield_validators={'product': 'uncertainties_validator',
                                      'quantiy': 'uncertainties_validator',
                 },
                 widget=RecordsWidget(
                     label = _("Uncertainty"),
                     description=_("Product item for this kit template"),
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
    FixedPointField('VAT',
        schemata='Price',
        default_method='getDefaultVAT',
        widget = DecimalWidget(
            label=_("VAT %"),
            description=_("Enter percentage value eg. 14.0"),
        ),
    ),
    FixedPointField('Price',
        schemata='Price',
        default='0.00',
        widget = DecimalWidget(
            label=_("Price excluding VAT"),
        )
    ),
    ComputedField('VATAmount',
        expression = 'context.getVATAmount()',
        widget = ComputedWidget(
            label=_("VAT"),
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('TotalPrice',
        expression = 'context.getTotalPrice()',
        widget = ComputedWidget(
            label=_("Total price"),
            visible = {'edit':'hidden', }
        ),
    ),
    FixedPointField('Cost',
        schemata='Price',
        default_method='getCost',
        widget = DecimalWidget(
            label=_("Cost"),
            description=_("Cost to client"),
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class KitTemplate(BaseContent):
    security = ClassSecurityInfo()
    implements(IKitTemplate)
    schema = schema
    
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

    security.declarePublic('getDefaultVAT')
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

registerType(KitTemplate, config.PROJECTNAME)
