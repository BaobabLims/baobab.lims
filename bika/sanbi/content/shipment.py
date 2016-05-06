from AccessControl import ClassSecurityInfo
from zope.interface import implements
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi import config
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
import sys
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.sanbi.interfaces import IShipment
from Products.CMFPlone.interfaces import IConstrainTypes

from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget


from Products.CMFCore import permissions

schema = BikaSchema.copy() + Schema((
    StringField(
        'ShipmentID',
        searchable=True,
        mode='rw',
        required=1,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            label=_("Shipment ID"),
            size=30,
            visible={'view': 'visible', 'edit': 'visible'},
        )

    ),

    TextField('DeliveryAddress',
        required=1,
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Delivery Address"),
            append_only=True,
        ),
    ),
    TextField('Shipping Address',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Shipping Address"),
            append_only=True,
        ),
    ),
    TextField('BillingAddress',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Billing Address"),
            append_only=True,
        ),
    ),

    TextField('CourierInstructions',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Courier Instructions"),
            append_only=True,
        ),
    ),

    StringField('ShipmentConditions',
        widget = StringWidget(
            label=_("Shipment Conditions"),
            description=_("Eg: Fragile, chilled, room temp"),
            size=30,

        )
    ),
    ReferenceField(
        'Attachment',
        multiValued=1,
        allowed_types=('Attachment',),
        referenceClass=HoldingReference,
        relationship='PackagingOutline',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ComputedWidget(
            label=_("Packaging Outline"),
            visible={'edit': 'invisible',
                     'view': 'invisible',
                     },
        )
    ),
    DateTimeField('ShippingDate',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Shipping Date',
            size=20
        ),
    ),

    DateTimeField('DateAssembled',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Date Assembled',
            description=_("Provide the expected expiry date of the kit product."),
            size=20
        ),
    ),

    DateTimeField('DateDispatched',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Date Dispatched',
            size=20
        ),
    ),

    DateTimeField('DateDelivered',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Date Delivered',
            description=_("Provide the expected expiry date of the kit product."),
            size=20
        ),
    ),
    ReferenceField('Courier',
       vocabulary_display_path_bound = sys.maxint,
       allowed_types=('Supplier',),
       relationship='ShipmentSupplier',
       referenceClass=HoldingReference,
       required=True,
       widget=bika_ReferenceWidget(
            label = _("Courier"),
            size=30,
            catalog_name='bika_setup_catalog',
            showOn=True,
            description=_("Start typing to filter the list of available couriers."),
        ),
    ),

    ReferenceField('Kit',
       allowed_types=('Kit',),
       relationship='ShipmentKit',
       required=False,
       widget=bika_ReferenceWidget(
            label = _("Kit"),
            size=30,
            showOn=True,
            description=_("Start typing to filter the list of available kits to ship."),
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'id', 'width': '20', 'label': _('Kit ID'), 'align': 'left'},
                      {'columnName': 'location', 'width': '20', 'label': _('Location'), 'align': 'left'},
                      ],
        ),
    ),
    StringField('TrackingURL',
        widget = StringWidget(
            label=_("Tracking URL"),
            size=30,
        )
    ),
    FixedPointField('ShippingCost',
        widget=DecimalWidget(
            label=_("Shipping Cost"),
        ),
    ),

    FixedPointField('Weight',
        widget=DecimalWidget(
            label=_("Weight"),
            description=_("Enter the weight in Kg"),
        ),
    ),
    StringField('Volume',
        widget = StringWidget(
            label=_("Volume"),
            description=_("Enter dimensions of the package (lxbxh) in CM"),
            size=30,
        )
    ),

))
schema['title'].required = False
schema['title'].widget.visible = False
schema.moveField('ShipmentID', before='description')
schema.moveField('Courier', before='description')
schema.moveField('Kit', after='Courier')
schema.moveField('TrackingURL', before='description')
schema.moveField('ShippingDate', before='description')


class Shipment(BaseContent):
    security = ClassSecurityInfo()
    implements(IShipment, IConstrainTypes)
    schema = schema

    _at_rename_after_creation = True

    def getOwnShippingId(self):
        return self.ShipmentID

    def getShipmentId(self):
        return self.getId()

registerType(Shipment, config.PROJECTNAME)
