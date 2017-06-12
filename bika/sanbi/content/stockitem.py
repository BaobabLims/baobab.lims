from plone.indexer import indexer
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.sanbi.interfaces import IStockItem, IStockItemStorage
from bika.sanbi.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
import sys


@indexer(IStockItem)
def get_product_uid(instance):
    return instance.getProduct().UID()


schema = BikaSchema.copy() + Schema((
    ReferenceField(
        'Product',
        required=1,
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=('Product'),
        relationship='StockItemProduct',
        widget=bika_ReferenceWidget(
            label=_("Product"),
            catalog_name='bika_setup_catalog',
            showOn=False,
            description=_("Start typing to filter the list of available products."),
        ),
    ),

    ReferenceField(
        'StorageLocation',
        allowed_types=('UnmanagedStorage', 'StoragePosition'),
        relationship='ItemStorageLocation',
        widget=bika_ReferenceWidget(
            label=_("Storage Location"),
            description=_("Location where item is kept"),
            size=40,
            visible={'edit': 'visible', 'view': 'visible'},
            catalog_name='bika_setup_catalog',
            showOn=True,
            base_query={'inactive_state': 'active',
                        'review_state': 'available',
                        'object_provides': IStockItemStorage.__identifier__},
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Title', 'width': '50', 'label': _('Title')},
                      {"columnName": "Hierarchy", "align": "left", "label": "Hierarchy", "width": "50"}
                      ],
        )
    ),

    ComputedField(
        'ProductTitle',
        expression='context.getProduct().Title()',
        widget=ComputedWidget(
            label=_("Product Title"),
            visible={'edit': 'hidden'}
        ),
    ),

    ComputedField(
        'ProductID',
        expression="context.getProduct() and context.getProduct().getId() or ''",
        widget=ComputedWidget(
            label=_("Product Title"),
            visible={'edit': 'hidden'}
        ),
    ),

    StringField(
        'orderId',
        widget=StringWidget(
            label=_("Invoice Number"),
        )
    ),

    StringField(
        'batchId',
        widget=StringWidget(
            label=_("Batch Id"),
        )
    ),

    StringField(
        'receivedBy',
        widget=StringWidget(
            label=_("Received By"),
            description="Provide full-name of the person receiving the current product in stock."
        )
    ),

    DateTimeField(
        'dateReceived',
        searchable=1,
            widget=bika_DateTimeWidget(
            label='Date Received'
        ),
    ),

    DateTimeField(
        'dateOpened',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Date Opened'
        ),
    ),

    DateTimeField(
        'expiryDate',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Expiry Date'
        ),
    ),

    DateTimeField(
        'disposalDate',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Disposal Date'
        ),
    ),
))

schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].schemata = 'default'
schema['description'].widget.visible = True
schema.moveField('Product', before='description')


class StockItem(BaseContent):
    implements(IStockItem)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)
        # self.at_post_create_script()

    def getProductTitle(self):
        return self.getProduct() and self.getProduct().Title() or ''

    def getStockItemId(self):
        return self.getId()

    def is_stored(self):
        return self.getStorageLocation() is not None


registerType(StockItem, PROJECTNAME)
