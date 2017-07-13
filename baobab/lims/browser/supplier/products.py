from baobab.lims.controlpanel.bika_products import ProductsView


class SupplierProductsView(ProductsView):

    def __init__(self, context, request):
        # import pdb;
        # pdb.set_trace()
        ProductsView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.context_actions = {}

    def folderitems(self):
        items = ProductsView.folderitems(self)
        uidsup = self.context.UID()
        outitems = []
        for x in range(len(items)):
            obj = items[x].get('obj', None)
            for uid in obj.getSuppliers():
                if uid == uidsup:
                    after_icons = ''
                    if obj.getHazardous():
                        after_icons = ("<img src='++resource++bika.lims.images/"
                                       "hazardous.png' title='Hazardous'>")
                    items[x]['replace']['Title'] = "<a href='%s'>%s</a>&nbsp;%s" % \
                         (items[x]['url'], items[x]['Title'], after_icons)
                    outitems.append(items[x])
        return outitems