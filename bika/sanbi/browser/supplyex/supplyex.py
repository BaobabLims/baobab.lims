from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from operator import itemgetter, methodcaller

from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView

from Products.ATContentTypes.lib import constraintypes

class View(BrowserView):

    template = ViewPageTemplateFile('templates/supplyex_view.pt')
    title = _('Supply Ex')

    def __call__(self):
        context = self.context
        portal = self.portal
        setup = portal.bika_setup
        # Disable the add new menu item
        context.setConstrainTypesMode(1)
        context.setLocallyAllowedTypes(())
        # Collect general data
        self.id = context.getId()
        self.title = context.Title()
        self.kittemplate_title = context.getKitTemplate().Title()
        self.quantity = context.getQuantity()

        self.subtotal = '%.2f' % context.getKitTemplate().getSubtotal()
        self.vat = '%.2f' % context.getKitTemplate().getVATAmount()
        self.total = '%.2f' % context.getKitTemplate().getTotal()

        items = context.getKitTemplate().kittemplate_lineitems
        self.items = []
        for item in items:
            prodtitle = item['Product']
            price = float(item['Price'])
            vat = float(item['VAT'])
            qty = float(item['Quantity'])
            self.items.append({
                'title': prodtitle,
                'price': price,
                'vat': vat,
                'quantity': qty,
                'totalprice': '%.2f' % (price * qty)
            })
        self.items = sorted(self.items, key=itemgetter('title'))
        # Render the template
        return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/supplyex_edit.pt')
    field = ViewPageTemplateFile('templates/row_field.pt')

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup

        if 'submit' in request:
            #pdb.set_trace()
            # ***** Is it a hack this line?
            context.aq_parent.setConstrainTypesMode(constraintypes.DISABLED)
            # *****
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return
        else:
            # Render the template
            return self.template()

    def get_fields_with_visibility(self, visibility, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:
                fields.append(field)
        return fields

    def computeNumberKits(self):
        """Implement me later"""

    def updateStockItems(self):
        """Implement me later"""

class PrintView(View):

    template = ViewPageTemplateFile('templates/supplyex_print.pt')

    def __call__(self):
        return View.__call__(self)
