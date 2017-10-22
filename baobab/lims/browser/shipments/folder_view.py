from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from baobab.lims import bikaMessageFactory as _
from baobab.lims.permissions import ManageKits


class ShipmentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.contentFilter = {'portal_type': 'Shipment',
                              'sort_on': 'sortable_title'}
        request.set('disable_plone.rightcolumn', 1)
        self.context_actions = {}
        self.catalog = 'bika_catalog'
        self.title = self.context.translate(_("Shipments"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipments_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        if self.context.portal_type == 'Shipments':
            self.request.set('disable_border', 1)

        self.columns = {
            'ShipmentID': {'title': _('Shipment ID'),
                           'index': 'sortable_title',
                           'toggle': True},
            'Project': {'title': _('Project'),
                        'toggle': True},
            'Courier': {'title': _('Courier'),
                        'toggle': True},
            'TrackingURL': {'title': _('Tracking URL'),
                            'toggle': True},
            'ShippingDate': {'title': _('Shipping Date'),
                             'toggle': True},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('All'),
                'contentFilter': {},
                'transitions': [{'id': 'deactivate'},
                                {'id': 'dispatch_shipment'},
                                {'id': 'receive_shipment'},
                                {'id': 'collect'},
                                {'id': 'receive_back'}],
                'columns': [
                    'ShipmentID',
                    'Project',
                    'Courier',
                    'TrackingURL',
                    'ShippingDate',
                    'state_title'
                ]
            },
            {
                'id': 'pending',
                'title': _('Pending'),
                'contentFilter': {'review_state': 'pending'},
                'transitions': [{'id': 'deactivate'},
                                {'id': 'dispatch_shipment'}],
                'columns': [
                    'ShipmentID',
                    'Project',
                    'Courier',
                    'TrackingURL',
                    'ShippingDate',
                    'state_title'
                ]
            },
            {
                'id': 'dispatched',
                'title': _('Dispatched'),
                'contentFilter': {'review_state': 'dispatched'},
                'transitions': [{'id': 'deactivate'},
                                {'id': 'receive_shipment'}],
                'columns': [
                    'ShipmentID',
                    'Project',
                    'Courier',
                    'TrackingURL',
                    'ShippingDate',
                    'state_title'
                ]
            },
            {
                'id': 'received',
                'title': _('Received'),
                'contentFilter': {'review_state': 'received'},
                'transitions': [{'id': 'deactivate'},
                                {'id': 'collect'}],
                'columns': [
                    'ShipmentID',
                    'Project',
                    'Courier',
                    'TrackingURL',
                    'ShippingDate',
                    'state_title'
                ]
            },
            {
                'id': 'to_collect',
                'title': _('To collect'),
                'contentFilter': {'review_state': 'to_collect'},
                'transitions': [{'id': 'deactivate'},
                                {'id': 'receive_back'}],
                'columns': [
                    'ShipmentID',
                    'Project',
                    'Courier',
                    'TrackingURL',
                    'ShippingDate',
                    'state_title'
                ]
            },
            {
                'id': 'received_back',
                'title': _('Received Back'),
                'contentFilter': {'review_state': 'received_back'},
                'transitions': [{'id': 'deactivate'}],
                'columns': [
                    'ShipmentID',
                    'Project',
                    'Courier',
                    'TrackingURL',
                    'ShippingDate',
                    'state_title'
                ]
            },
        ]

    def __call__(self):

        mtool = getToolByName(self.context, 'portal_membership')

        if mtool.checkPermission(ManageKits, self.context) and \
                self.context.portal_type == 'Project':
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Shipment',
                'icon': '++resource++bika.lims.images/add.png'
            }


        return super(ShipmentsView, self).__call__()

    def folderitems(self):
        items = super(ShipmentsView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['ShipmentID'] = obj.getId()
            if self.context.portal_type == 'Shipments':
                items[x]['replace']['Project'] = "<a href='%s'>%s</a>" % \
                                                 (obj.aq_parent.absolute_url(),
                                                  obj.aq_parent.Title())
            items[x]['ShippingDate'] = self.ulocalized_time(
                obj.getShippingDate())
            items[x]['Courier'] = obj.getCourier()
            items[x]['replace']['ShipmentID'] = "<a href='%s'>%s</a>" % \
                                                (items[x]['url'],
                                                 obj.getId())
        return items
