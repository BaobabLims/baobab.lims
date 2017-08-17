from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter, methodcaller
from Products.CMFPlone.utils import _createObjectByType
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from DateTime import DateTime

from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import tmpID
from bika.lims.utils import to_utf8
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView

from baobab.lims.browser.inventory import store_item_unmanaged_storage


class OrderView(BrowserView):
    template = ViewPageTemplateFile('templates/order_view.pt')
    title = _('Inventory Order')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def stored_quantity_items(self, product):
        """ When the client1 restarted the stored quantity in order_lineitems is reset to 0.
            Here we use the stock-items quantities linked to the order.
        """
        brains = self.bika_setup_catalog(
            portal_type='StockItem',
            getProductUID=product.UID())

        quantity = 0
        for brain in brains:
            item = brain.getObject()
            if item.getOrderId() == self.context.getId():
                quantity += item.getQuantity()

        return quantity

    def __call__(self):
        portal = self.portal
        setup = portal.bika_setup
        # Disabling the add new menu item
        self.context.setConstrainTypesMode(1)
        self.context.setLocallyAllowedTypes(())
        # Collect general data
        self.orderDate = self.ulocalized_time(self.context.getOrderDate())
        # self.supplier = context.getsupplier()
        # self.supplier = self.supplier.getFullname() if self.supplier else ''
        self.subtotal = '%.2f' % self.context.getSubtotal()
        self.vat = '%.2f' % self.context.getVATAmount()
        self.total = '%.2f' % self.context.getTotal()
        # Set the title
        self.title = self.context.Title()
        # Collect order item data
        items = self.context.order_lineitems
        # products = context.aq_parent.objectValues('Product')
        products = self.context.get_supplier_products()
        self.items = []
        for item in items:
            product_id = item['Product']
            product = [p for p in products if p.getId() == product_id][0]
            price = float(item['Price'])
            vat = float(item['VAT'])
            qty = item['Quantity']
            item['Stored'] = item['Stored'] and item['Stored'] or self.stored_quantity_items(product)
            stored = item['Stored']
            all_stored = qty == stored
            self.items.append({
                'title': product.Title(),
                'description': product.Description(),
                'unit': product.getUnit(),
                'price': price,
                'vat': '%s%%' % vat,
                'quantity': qty,
                'totalprice': '%.2f' % (price * qty),
                'prodid': product_id,
                'stored': stored,
                'all_stored': all_stored,
            })

        self.items = sorted(self.items, key=itemgetter('title'))
        # Render the template
        return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/order_edit.pt')
    field = ViewPageTemplateFile('templates/row_field.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup
        catalog = getToolByName(context, 'bika_setup_catalog')
        brains = catalog(portal_type='Product', inactive_state='active')
        # Allow adding items to this context
        context.setConstrainTypesMode(0)
        # Collect the products
        # products = context.aq_parent.objectValues('Product')
        products = context.get_supplier_products()
        # Handle for submission and regular request
        if 'submit' in request:
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()
            # Clear the old line items
            context.order_lineitems = []
            # Process the order item data
            data = []
            for e in request.form.items():
                if e[0].startswith('product_'):
                    data.append(e)
            data.sort(key=lambda tup: tup[0])

            for prod_id, qty in data:
                prod_id = prod_id.replace('product_', '')
                product = [pro for pro in products if pro.getId() == prod_id][0]
                context.order_lineitems.append(
                        {'Product': prod_id,
                         'Quantity': int(qty),
                         'Stored': 0,
                         'Price': product.getPrice(),
                         'VAT': product.getVAT()})

            # Redirect to the list of orders
            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return
        else:
            self.orderDate = context.Schema()['OrderDate']
            self.subtotal = '%.2f' % context.getSubtotal()
            self.vat = '%.2f' % context.getVATAmount()
            self.total = '%.2f' % context.getTotal()
            # Prepare the products
            items = context.order_lineitems
            self.products = []
            products = sorted(products, key = methodcaller('Title'))
            for product in products:
                item = [o for o in items if o['Product'] == product.getId()]
                quantity = item[0]['Quantity'] if len(item) > 0 else 0

                self.products.append({
                    'id': product.getId(),
                    'title': product.Title(),
                    'description': product.Description(),
                    'unit': product.getUnit(),
                    'price': product.getPrice(),
                    'vat': '%s%%' % product.getVAT(),
                    'quantity': quantity,
                    'total': (float(product.getPrice()) * float(quantity)),
                })
            # Render the template
            return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class PrintView(OrderView):

    template = ViewPageTemplateFile('templates/order_print.pt')
    view_template = ViewPageTemplateFile('templates/order_view.pt')

    def __init__(self, context, request):
        OrderView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        self.orderDate = self.context.getOrderDate()
        # products = context.aq_parent.objectValues('Product')
        products = self.context.get_supplier_products()
        items = self.context.order_lineitems
        self.items = []
        for item in items:
            prodid = item['Product']
            product = [pro for pro in products if pro.getId() == prodid][0]
            price = float(item['Price'])
            vat = float(item['VAT'])
            qty = item['Quantity']
            self.items.append({
                'title': product.Title(),
                'description': product.Description(),
                'unit': product.getUnit(),
                'price': price,
                'vat': '%s%%' % vat,
                'quantity': qty,
                'totalprice': '%.2f' % (price * qty)
            })
        self.items = sorted(self.items, key = itemgetter('title'))
        self.subtotal = '%.2f' % self.context.getSubtotal()
        self.vat = '%.2f' % self.context.getVATAmount()
        self.total = '%.2f' % self.context.getTotal()
        self.supplier = self._supplier_data()
        return self.template()

    def _supplier_data(self):
        data = {}
        supplier = self.context.aq_parent
        if supplier:
            data['obj'] = supplier
            data['id'] = supplier.id
            data['title'] = supplier.Title()
            data['url'] = supplier.absolute_url()
            data['name'] = to_utf8(supplier.getName())
            data['phone'] = to_utf8(supplier.getPhone())
            data['fax'] = to_utf8(supplier.getFax())

            supplier_address = supplier.getPostalAddress()
            if supplier_address:
                _keys = ['address', 'city', 'state', 'zip', 'country']
                _list = ["<div>%s</div>" % supplier_address.get(v) for v in _keys
                         if supplier_address.get(v)]
                supplier_address = "".join(_list)
            else:
                supplier_address = ''
            data['address'] = to_utf8(supplier_address)
            data['email'] = to_utf8(supplier.getEmailAddress())
        return data

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class OrderStore2(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def create_stock_items(self, product, quantity):

        folder = self.context.bika_setup.bika_stockitems
        item = _createObjectByType('StockItem', folder, tmpID())
        item.setTitle(product.Title() + '-' + self.context.getId())
        item.setProduct(product)
        item.setOrderId(self.context.getId())
        item.setDateReceived(DateTime())
        item.setQuantity(quantity)
        item.unmarkCreationFlag()
        renameAfterCreation(item)
        # Manually reindex stock item in catalog
        self.context.bika_setup_catalog.reindexObject(item)

        # Update product quantity
        product_quantity = product.getQuantity() and product.getQuantity() or 0
        product.setQuantity(product_quantity + quantity)

        return item

    def __call__(self):

        self.context.setConstrainTypesMode(0)

        if not 'submit' in self.request:
            return self.request.response.redirect(self.context.absolute_url_path())

        # products = context.aq_parent.objectValues('Product')
        products = self.context.get_supplier_products()
        uc = getToolByName(self.context, 'uid_catalog')

        index = 0
        for name, _ in sorted(self.request.form.iteritems(), key=lambda (k, v): (k, v)):

            if not name.startswith('storage-'):
                continue

            if 'StorageInventory_uid' in self.request.form:
                if isinstance(self.request.form['StorageInventory_uid'], list):
                    uid = self.request.form['StorageInventory_uid'][index]
                    index += 1
                else:
                    uid = self.request.form['StorageInventory_uid']

                if not uid:
                    continue

                product_id = name.lstrip('storage-')

                nid = 'number-' + product_id
                if nid in self.request.form and self.request.form[nid]:
                    quantity_to_store = int(self.request.form[nid])
                else:
                    continue

                # Validate number and storage levels
                quantity_ordered = [q['Quantity'] for q in self.context.order_lineitems if q['Product'] == product_id][0]
                if quantity_to_store < 1 or quantity_to_store > quantity_ordered or quantity_ordered < 1:
                    continue

                # create stock-items
                product = [p for p in products if p.getId() == product_id][0]
                stock_item = self.create_stock_items(product, quantity_to_store)

                # store item in inventory storage
                container = [c.getObject() for c in uc(UID=uid)][0]

                if container.portal_type == 'UnmanagedStorage':
                    message = store_item_unmanaged_storage(self.context, container, stock_item, quantity_to_store,
                                                           product_id)
                else:
                    raise RuntimeError('This should not happen. Stock items could be stored only '
                                       'in unmanaged storage type.')

                if message:
                    self.context.plone_utils.addPortalMessage(_(message), 'error')
                    continue

        return self.request.response.redirect(self.context.absolute_url_path())


class OrderStore(BrowserView):
    """Store order's stock items in storage.
    """
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup
        # Allow adding items to this context
        context.setConstrainTypesMode(0)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        uc = getToolByName(context, 'uid_catalog')
        catalog = [pi.getObject() for pi in bsc(portal_type='StockItem')]
        # Remaining stock items of this order
        stock_items = [pi for pi in catalog
                      if (pi.getOrderId() == self.context.getId() and
                          pi.is_stored() is False)]
        # Organize items as per their product
        products_dict = {}
        for pi in stock_items:
            product_id = pi.getProduct().getId()
            if product_id not in products_dict:
                products_dict[product_id] = []
            products_dict[product_id].append(pi)
        # Product names against their IDs used for error messages
        product_names = {}
        # products = context.aq_parent.objectValues('Product')
        products = context.get_supplier_products()
        for pr in products:
            product_names[pr.getId()] = pr.Title()

        if not 'submit' in request:
            request.response.redirect(context.absolute_url_path())
            return
        # Process form inputs
        portal_factory = getToolByName(context, 'portal_factory')
        context = portal_factory.doCreate(context, context.id)
        context.processForm()

        index = 0
        for name, _ in sorted(request.form.iteritems(), key=lambda (k,v): (k, v)):

            if not name.startswith('storage-'):
                continue

            if 'StorageInventory_uid' in request.form:
                if isinstance(request.form['StorageInventory_uid'], list):
                    uid = request.form['StorageInventory_uid'][index]
                    index += 1
                else:
                    uid = request.form['StorageInventory_uid']

                if not uid:
                    continue

                product_id = name.lstrip('storage-')
                product_name = product_names[product_id]

                stock_items = products_dict[product_id]

                nid = 'number-' + product_id
                if nid in request.form and request.form[nid]:
                    number = int(request.form[nid])
                else:
                    continue

                # Validate number and storage levels
                if number < 1:
                    continue

                message = ''

                if len(stock_items) != 1:
                    message = _('Length of stock items should be 1. This should not happen.')

                if number > stock_items[0].getQuantity():
                    message = _('The quantity to store entered for ' + product_name + ' is invalid.')

                stock_item = stock_items[0]
                container = [c.getObject() for c in uc(UID=uid)][0]

                if container.portal_type == 'UnmanagedStorage':
                    message = store_item_unmanaged_storage(self.context, container, stock_item, number,
                                                           product_id)
                else:
                    raise RuntimeError('This should not happen. Stock items could be stored only '
                                       'in unmanaged storage type.')

                if message:
                    self.context.plone_utils.addPortalMessage(_(message), 'error')
                    continue

        request.response.redirect(context.absolute_url_path())
        return


class OrderPathBarViewlet(ViewletBase):
    """Viewlet for overriding breadcrumbs in Order View"""

    index = ViewPageTemplateFile('templates/path_bar.pt')

    def update(self):
        super(OrderPathBarViewlet, self).update()
        self.is_rtl = self.portal_state.is_rtl()
        breadcrumbs = getMultiAdapter((self.context, self.request),
                                      name='breadcrumbs_view').breadcrumbs()
        breadcrumbs[2]['absolute_url'] += '/orders'
        self.breadcrumbs = breadcrumbs
