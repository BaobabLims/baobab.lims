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
    ReferenceField(
        'Project',
        required=1,
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=('Project',),
        relationship='KitProject',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
           label=_("Project"),
           catalog_name='bika_catalog',
           size=30,
           render_own_label=True,
           showOn=True,
           description=_("Click and select project for the kit."),
        )
    ),

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
        )
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
        )
    ),

    IntegerField('QtyStored',
        mode="rw",
        required=1,
        default=0,
        widget=IntegerWidget(
            visible={'view': 'invisible', 'edit': 'invisible'},
        )
    ),

    ReferenceField('Location',
        required=1,
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=('StorageInventory',),
        relationship='KitInventory',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label=_("Location"),
            size=30,
            render_own_label=True,
            catalog_name='bika_setup_catalog',
            showOn=True,
            description=_("Start typing to filter the list of available Storage Inventories."),
            base_query={'inactive_state': 'active', 'object_provides': 'bika.sanbi.interfaces.IInventoryAssignable'},
            visible={'view': 'visible', 'edit': 'visible'}
        ),
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

    BooleanField(
        'FormsThere',
        required=1,
        default=False,
        widget=BooleanWidget(
            label="Form Added to Kit",
            description="It is necessary to add all forms describing the content of the kit.",
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible'}
        )
    ),

    StringField(
        'KitPrdUID',
        widget=StringWidget(
            description=_("The id of the corresponding produt of this kit."),
            visible={'view': 'invisible', 'edit': 'invisible'},
        )
    ),

    LinesField(
        'ItemPositions',
        widget=LinesWidget(
            visible=False
        )
    ),
))
schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].schemata = 'default'
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.render_own_label = True
schema.moveField('Prefix', before='description')
schema.moveField('Location', before='description')
schema.moveField('quantity', before='description')
schema.moveField('expiryDate', before='description')
schema.moveField('KitTemplate', before='Prefix')
schema.moveField('Project', before='KitTemplate')

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

    def at_post_create_script(self):
        """Execute once the object is created
        """
        self.title = self.getId()
        self.reindexObject()

    def workflow_script_complete(self):
        """Complete kit assembly
        """
        kittemplate = self.getKitTemplate()
        # "kit_name" will be used as product name
        kit_name = kittemplate.Title()
        kit_description = self.Description()
        # for product category we will use the one in kit template
        product_category = kittemplate.getCategory()
        kit_qty = self.getQuantity()
        #storage_conditions = kittemplate.getStorageConditions()
        kit_price = kittemplate.getPrice()
        kit_vat = kittemplate.getVAT()

        wf = getToolByName(self, 'portal_workflow')
        uids = self.getItemPositions()
        uc = getToolByName(self, 'uid_catalog')
        bsc = getToolByName(self, 'bika_setup_catalog')
        for uid in uids:
            brains = uc(UID=uid)
            position = brains[0].getObject()
            sid = position.getISID()
            si = bsc(portal_type='StockItem', id=sid)[0].getObject()
            product = si.getProduct()
            product.setQuantity(product.getQuantity() - 1)
            si.setQuantity(0)
            si.setIsStored(False)
            wf.doActionFor(si, 'discard')
            si.setStorageLevelID('')
            position.liberatePosition()

        # create kit assembly as product
        catalog = getToolByName(self, 'bika_setup_catalog')
        # TODO: WHY I ADDED THIS LINE?
        brains = catalog.searchResults({'portal_type': 'Product', 'title': kit_name})
        if len(brains) == 0:
            folder = self.bika_setup.bika_products
            product = _createObjectByType('Product', folder, tmpID())
            product.edit(
                title=kit_name,
                description=kit_description,
                Hazardous=True,
                Quantity=kit_qty,
                Price=kit_price,
                VAT=kit_vat,
                # StorageConditions=storage_conditions,
            )
            product.setCategory(product_category)
            product.unmarkCreationFlag()
            renameAfterCreation(product)
        else:
            product = brains[0].getObject()
            new_qty = product.getQuantity() + kit_qty
            product.edit(
                description=kit_description,
                Quantity=new_qty,
                Price=kit_price,
                VAT=kit_vat,
                # StorageConditions=storage_conditions,
            )
            product.reindexObject()

        self.setKitPrdUID(product.UID())

        # create kit quantity as stockitems
        folder = self.bika_setup.bika_stockitems
        for i in range(kit_qty):
            obj = _createObjectByType("StockItem", folder, tmpID())
            obj.edit(
                StockItemID='',
                description=product.Description(),
                location='',
                Quantity=1,
                orderId='',
                IsStored=False,
                dateManufactured=DateTime(),
                expiryDate=self.getExpiryDate(),
                title=product.Title()
            )
            obj.setProduct(product)
            obj.setDateReceived(DateTime())
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.bika_setup_catalog.reindexObject(obj)

    def workflow_script_deactivate(self):
        """DEACTIVATE ACTION"""
        # TODO: DO WE HAVE TO REMOVE QUANTITY FROM KIT-STOCKITEM WHEN THIS OBJECT IS DEACTIVATED?
        # TODO: MAY BE THIS WILL BE USEFUL TO GET THE STATUS OF AN OBJECT TOO:
        # context.portal_workflow.getInfoFor(context, 'review_state')
        workflowTool = getToolByName(self, "portal_workflow")
        status = workflowTool.getStatusOf("bika_kit_assembly_workflow", self)
        print status

registerType(Kit, config.PROJECTNAME)
