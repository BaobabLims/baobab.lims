from Products.CMFCore.utils import getToolByName
from bika.sanbi import bikaMessageFactory as _
from zope.interface.declarations import implements
from bika.sanbi.permissions import *
from bika.lims.browser.bika_listing import BikaListingView

from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView


class ShipmentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ShipmentsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Shipment',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Shipments"))
<<<<<<< HEAD
        self.icon = self.portal_url + "/++resource++bika.sanbi.images/shipment_icon_big.png"
=======
        self.icon = self.portal_url + "/++resource++bika.sanbi.images/shipment_big.png"
>>>>>>> master
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        self.columns = {
            'ShipmentID': {'title': _('Shipment ID'),
                      'index': 'sortable_title',
                      'toggle': True},
            'Courier': {'title': _('Courier'),
                       'toggle': True},
            'TrackingURL': {'title': _('Tracking URL'),
                       'toggle': True},
            'ShippingDate': {'title': _('Shipping Date'),
                       'toggle': True},
        }

        self.review_states = [
            {
                'id':'default',
                'title': _('All'),
                'contentFilter':{},
                'columns': ['ShipmentID', 'Courier', 'TrackingURL', 'ShippingDate']
            },
            {
                'id': 'pending',
                'title': _('Pending'),
                'contentFilter': {'review_state': 'pending'},
                'columns': ['ShipmentID', 'Courier', 'TrackingURL', 'ShippingDate']
            },
        ]

    def __call__(self):

        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddShipment, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Shipment',
                'icon': '++resource++bika.lims.images/add.png'
            }
        if mtool.checkPermission(ManageShipments, self.context):
            stat = self.request.get("%s_review_state"%self.form_id, 'default')
            self.show_select_column = stat != 'all'
        return super(ShipmentsView, self).__call__()

    def folderitems(self):
        items = super(ShipmentsView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['ShipmentID'] = obj.getOwnShippingId()
            items[x]['ShippingDate'] = self.ulocalized_time(obj.getShippingDate())
            items[x]['Courier'] = obj.getCourier().getName()
            items[x]['replace']['ShipmentID'] = "<a href='%s'>%s</a>" % \
                (items[x]['url'], obj.getOwnShippingId())
        return items
