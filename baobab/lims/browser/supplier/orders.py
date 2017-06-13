from zope.interface import implements
from plone.app.layout.globals.interfaces import IViewView

from baobab.lims import bikaMessageFactory as _
from baobab.lims.browser.inventory.orderfolder import OrderFolderView


class SupplierOrdersView(OrderFolderView):
    implements(IViewView)

    def __init__(self, context, request):
        super(SupplierOrdersView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'InventoryOrder',
            'sort_on': 'sortable_title',
            'sort_order': 'reverse',
            'path': {
                'query': '/'.join(context.getPhysicalPath()),
                'level': 0
            }
        }
        self.context_actions = {
            _('Add'): {
                'url': 'createObject?type_name=InventoryOrder',
                'icon': '++resource++bika.lims.images/add.png'
            }
        }