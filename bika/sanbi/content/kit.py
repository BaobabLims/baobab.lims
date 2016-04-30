from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi import config
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
import sys
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.sanbi.interfaces import IKit
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils import tmpID
from bika.lims.idserver import renameAfterCreation
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget

from Products.CMFCore import permissions

schema = BikaSchema.copy() + Schema((
    StringField(
        'Prefix',
        searchable=True,
        mode="rw",
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            label=_("Prefix"),
            description=_("Provide a prefix for the ids. The default is KIT-."),
            size=30,
            render_own_label=True,
            visible={'view': 'visible', 'edit': 'visible'},
            placeholder="KIT-",
        )
    ),
    ReferenceField('KitTemplate',
        required=1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types=('KitTemplate',),
        relationship='KitAssemblyTemplate',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label = _("Kit template"),
            size=30,
            render_own_label=True,
            catalog_name='bika_setup_catalog',
            showOn=True,
            description=_("Start typing to filter the list of available kit templates."),
        ),
    ),
    IntegerField('quantity',
        mode="rw",
        required=1,
        default=1,
        widget = IntegerWidget(
            label=_("Quantity"),
            render_own_label=True,
            description=_("The number of kit templates to assemble. eg. 15, 100"),
            visible={'view': 'visible', 'edit': 'visible'},
        ),
    ),
    StringField('location',
        widget = StringWidget(
            label=_("Location"),
            size=30,
            render_own_label=True
        )
    ),
    DateTimeField('expiryDate',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Expiry Date',
            description=_("Provide the expected expiry date of the kit product."),
            render_own_label=True,
            size=20
        ),
    ),
    BooleanField(
        'IsStored',
        default=False,
        widget=BooleanWidget(visible=False),
    ),
    ReferenceField(
        'Attachment',
        multiValued=1,
        allowed_types=('Attachment',),
        referenceClass=HoldingReference,
        relationship='KitAttachment',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ComputedWidget(
            visible={'edit': 'invisible',
                     'view': 'invisible',
                     },
        )
    ),
    TextField('Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Remarks"),
            append_only=True,
        ),
    ),
))
schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].schemata = 'default'
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.render_own_label = True
schema.moveField('Prefix', before='description')
schema.moveField('location', before='description')
schema.moveField('quantity', before='description')
schema.moveField('expiryDate', before='description')
schema.moveField('KitTemplate', before='Prefix')

class Kit(BaseContent):
    security = ClassSecurityInfo()
    implements(IKit, IConstrainTypes)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getKitId(self):
        return self.getId()

    def getKitTemplateTitle(self):
        return self.getKitTemplate().Title()

    def workflow_script_complete(self):
        """Complete kit assembly
        """
        kittemplate = self.getKitTemplate()
        # "kit_name" will be used as product name
        kit_name = kittemplate.Title()
        kit_description = self.Description()
        # for product category we will use the one in kit template
        product_category = kittemplate.getCategory()
        kit_quantity = self.getQuantity()
        storage_conditions = kittemplate.getStorageConditions()
        kit_price = kittemplate.getPrice()
        kit_vat = kittemplate.getVAT()

        # create kit assembly as product
        catalog = getToolByName(self, 'bika_setup_catalog')
        brains = catalog.searchResults({'portal_type': 'Product', 'title': kit_name})
        if len(brains) == 0:
            folder = self.bika_setup.bika_products
            obj = _createObjectByType('Product', folder, tmpID())
            obj.edit(
                title=kit_name,
                description=kit_description,
                Hazardous=True,
                Quantity=kit_quantity,
                Price=kit_price,
                VAT=kit_vat,
                StorageConditions=storage_conditions,
            )
            obj.setCategory(product_category)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
        else:
            obj = brains[0].getObject()
            new_qty = obj.getQuantity() + kit_quantity
            obj.edit(
                description=kit_description,
                Quantity=new_qty,
                Price=kit_price,
                VAT=kit_vat,
                StorageConditions=storage_conditions,
            )
            # TODO: Check if self or obj to be reindexed
            obj.reindexObject()

    def workflow_script_store(self):
        """Store kit assembled
        """
        kittemplate = self.getKitTemplate()
        kit_name = kittemplate.Title()
        expiry_date = self.getExpiryDate()
        catalog = getToolByName(self, 'bika_setup_catalog')
        brains = catalog.searchResults({'portal_type': 'Product', 'title': kit_name})
        if len(brains) == 1:
            product = brains[0].getObject()
            folder = self.bika_setup.bika_stockitems
            # TODO: BEFORE CREATE THE STOCKITEM WE'VE TO CHECK IF EXISTS BEFORE. IF SO THEN WE'VE JUST
            # TODO: TO ADJUST THE STOCK QUANTITY
            obj = _createObjectByType("StockItem", folder, tmpID())
            obj.edit(
                StockItemID='',
                description=product.Description(),
                location='',
                Quantity=product.getQuantity(),
                orderId='',
                IsStored=True,
                dateManufactured=DateTime(),
                expiryDate=expiry_date,
            )
            obj.setProduct(product)
            obj.setDateReceived(DateTime())
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.bika_setup_catalog.reindexObject(obj)
        else:
            # TODO: if len(brains) == 0 we have to raise an error. It should be 1.
            print "Error: Number of products with {} name should be 1".format(kit_name)

    def workflow_script_deactivate(self):
        """DEACTIVATE ACTION"""
        # TODO: DO WE HAVE TO REMOVE QUANTITY FROM KIT-STOCKITEM WHEN THIS OBJECT IS DEACTIVATED?
        # TODO: MAY BE THIS WILL BE USEFUL TO GET THE STATUS OF AN OBJECT TOO:
        # context.portal_workflow.getInfoFor(context, 'review_state')
        workflowTool = getToolByName(self, "portal_workflow")
        status = workflowTool.getStatusOf("bika_kit_assembly_workflow", self)
        print status

registerType(Kit, config.PROJECTNAME)
