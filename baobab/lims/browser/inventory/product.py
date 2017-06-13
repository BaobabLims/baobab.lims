import json

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.lims.browser.multifile import MultifileView
from bika.lims import bikaMessageFactory as _


class ProductMultifileView(MultifileView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ProductMultifileView, self).__init__(context, request)
        self.show_workflow_action_buttons = False
        self.title = self.context.translate(_("Product Files"))
        self.description = "Different interesting documents and files to be attached to the product"

class ProductStorageView(BrowserView):
    """Show graphic layout of available and occupied positions.
        """
    template = ViewPageTemplateFile("templates/product_by_storages.pt")
    title = _("Product by storages")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.request.set('disable_plone.rightcolumn', 1)

    def __call__(self):
        return self.template()

class ProductQuantityByStorage():
    """
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @staticmethod
    def _add_entry_to_dict(d, key):
        if key in d:
            d[key] += 1
        else:
            d[key] = 1

        return d

    def __call__(self):
        stock_items = self.context.getBackReferences("StockItemProduct")
        ret = []
        tmp = {}
        for si in stock_items:
            location = si.getStorageLocation()
            if not location: continue
            if location.portal_type == 'UnmanagedStorage':
                hierarchy = location.getHierarchy()
                self._add_entry_to_dict(tmp, hierarchy)
            if location.portal_type == 'ManagedStorage':
                hierarchy = location.aq_parent.getHierarchy()
                self._add_entry_to_dict(tmp, hierarchy)

        tmp = sorted(tmp.items(), key=lambda x: x[0])
        for e in tmp:
            ret.append({'title': e[0], 'quantity': e[1]})
        return json.dumps(ret)