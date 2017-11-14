from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.schema import ValidationError
from DateTime import DateTime

from baobab.lims.browser.project import get_first_sampletype
from baobab.lims.browser.project.util import SampleGeneration
from baobab.lims.interfaces import IUnmanagedStorage, IStoragePosition, IManagedStorage
from baobab.lims.permissions import ManageKits

class AddKitsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_kits_viewlet.pt")

    def render(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if checkPermission(ManageKits, self.context) and self.request.URL.endswith('kits'):
            return self.index()
        else:
            return ''


class AddKitsSubmitHandler(BrowserView):
    """
    """
    def __init__(self, context, request):
        super(AddKitsSubmitHandler, self).__init__(context, request)
        self.context = context
        self.request = request
        self.form = request.form
        self.uc = getToolByName(self.context, 'uid_catalog')
        self.bsc = self.bika_setup_catalog
        self.bc = self.bika_catalog
        self.wf = self.portal_workflow
        self.samples_gen = SampleGeneration(self.form, self.context)
        self.sample_type = get_first_sampletype(self.context)

    def __call__(self):
        if "viewlet_submitted" in self.request.form:
            try:
                self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)
                return

            self.context.setConstrainTypesMode(constraintypes.DISABLED)

            kits = self.create_kits()

            msg = u'%s kits assembled.' % len(kits)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url() + '/kits')

    def get_kit_storage(self):
        """Take a list of UIDs from the form, and resolve to a list of Storages.
        Accepts ManagedStorage, UnmanagedStorage, or StoragePosition UIDs. Not used!
        """
        kit_storages = []
        form_uids = self.form['kit-storage-uids'].split(',')
        for uid in form_uids:
            brain = self.bsc(UID=uid)[0]
            instance = brain.getObject()
            # last-minute check if this storage is available
            if IUnmanagedStorage.providedBy(instance) \
                    or len(instance.get_free_positions()) > 0:
                kit_storages.append(instance)

        return kit_storages

    @staticmethod
    def count_storage_positions(storages):
        """Return the number of items that can be stored in storages.

        If any of these storages are "UnmanagedStorage" objects, then the
        result will be -1 as we cannot know how many items can be stored here.
        """
        count = 0
        for storage in storages:
            # If storage is an unmanaged storage, we no longer care about
            # "number of positions".
            if IUnmanagedStorage.providedBy(storage):
                return -1
            # If storage is a StoragePosition, simply increment the count.
            elif IStoragePosition.providedBy(storage):
                count += 1
            # If storage is a ManagedStorage, increment count for each
            # available StoragePosition
            elif IManagedStorage.providedBy(storage):
                count += storage.getFreePositions()
            else:
                raise ValidationError("Storage %s is not a valid storage type" %
                                      storage)
        return count

    def get_si_storages(self):
        """ return storage which could store stock-items
        """
        si_storage = []
        for uid in self.form['si-storage-uids'].split(','):
            brain = self.bsc(UID=uid)
            if not brain:
                raise ValidationError(u'Bad uid. This should not happen.')
            si_storage.append(brain[0].getObject())

        return si_storage

    def filter_stock_items_by_storage(self, items):
        """Return stock-items in the selected storage
        """
        si_storage = self.get_si_storages()
        stock_items = []
        for storage in si_storage:
            if IUnmanagedStorage.providedBy(storage):
                sis = storage.getBackReferences('ItemStorageLocation')
                stock_items += [si for si in sis if si in items]
            elif IManagedStorage.providedBy(storage):
                sis = storage.only_items_of_portal_type('StockItem')
                stock_items += [si for si in sis if si in items]

        return stock_items

    def product_stock_items(self, uid):
        """ stock items of a product uid
        """
        brains = self.bika_setup_catalog(
            portal_type='StockItem',
            getProductUID=uid,
            review_state='available')
        items = [b.getObject() for b in brains]

        return items

    def template_stock_items(self, template):
        """ Return stock-items of kit template's products
        """
        stock_items = []
        for product in template.getProductList():
            items = self.product_stock_items(product['product_uid'])
            items = self.filter_stock_items_by_storage(items)
            quantity_product = int(product['quantity'])
            quantity_stock_items = sum([item.getQuantity() for item in items])
            if quantity_stock_items < quantity_product:
                msg = u"There is insufficient stock available for the " \
                    u"product '%s'." % product['product']
                self.form_error(msg)
                raise ValidationError(msg)

            for item in items:
                if item.getQuantity() <= quantity_product:
                    quantity_product -= item.getQuantity()
                    item.setQuantity(0)
                    self.portal_workflow.doActionFor(item, 'use')
                else:
                    item.setQuantity(item.getQuantity() - quantity_product)
                    quantity_product = 0

                stock_items.append(item)

                if quantity_product == 0:
                    break

        return stock_items

    def assign_stock_items_to_kit(self, kit):
        """Find required stock-items, remove them from storage and assign them to kit.
        """
        template = kit.getKitTemplate()
        stock_items = self.template_stock_items(template)
        kit.setStockItems(stock_items)

    def update_quantity_products(self, kit):
        """ Update the products quantity after assigning stock-items to kit
        """
        template = kit.getKitTemplate()
        products = []
        for item in template.getProductList():
            product = self.bsc(UID=item['product_uid'])[0].getObject()
            products.append(product)
        for product in products:
            stock_items = product.getBackReferences("StockItemProduct")
            quantity = sum([item.getQuantity() for item in stock_items])
            product.setQuantity(quantity)
            product.reindexObject()

    def assign_kit_to_storage(self, kits, storages):
        """ assign position to created kits. Not used anymore!
        """
        for storage in storages:
            if IManagedStorage.providedBy(storage):
                free_positions = storage.get_free_positions()
                if len(kits) <= len(free_positions):
                    for i, kit in enumerate(kits):
                        kit.setStorageLocation(free_positions[i])
                        self.wf.doActionFor(free_positions[i], 'occupy')
                else:
                    for i, position in enumerate(free_positions):
                        kits[i].setStorageLocation(position)
                        self.wf.doActionFor(position, 'occupy')
                    kits = kits[len(free_positions):]
            elif IUnmanagedStorage.providedBy(storage):
                # Case of unmanaged storage there is no limit in storage until
                # user manually set the storage as full.
                for kit in kits:
                    kit.setStorageLocation(storage)

    def create_kits(self):
        """Create the new kits
        """
        prefix_text = self.form.get('kits-prefix-text', None)
        seq_start = int(self.form.get('seq-start', None))
        kit_count = int(self.form.get('kit-count', None))
        kit_template_uid = self.form.get('kit_template_uid', None)
        spec_per_kit = int(self.form.get('specimen-count', None))
        leading_zeros = self.form.get('kits-leading-zeros', [])
        kits = []
        # sample storage
        samples = []
        sample_storage = self.samples_gen.get_biospecimen_storages()
        for x in range(seq_start, seq_start + kit_count):
            id_template = prefix_text + '-' + str(x).zfill(len(leading_zeros) + 1)
            title_template = prefix_text + ' ' + str(x).zfill(len(leading_zeros) + 1)
            obj = api.content.create(
                container=self.context,
                type='Kit',
                id=id_template,
                title=title_template,
                KitTemplate=kit_template_uid,
                DateCreated=DateTime()
            )

            obj.setProject(obj.aq_parent)

            if kit_template_uid:
                self.assign_stock_items_to_kit(obj)
                self.update_quantity_products(obj)
            self.context.manage_renameObject(obj.id, id_template.format(id=x))
            kits.append(obj)

        # generate biospecimens
        for kit in kits:
            for i in range(spec_per_kit):
                sample = self.samples_gen.create_sample(kit, self.sample_type)
                samples.append(sample)
        self.samples_gen.store_samples(samples, sample_storage)

        return kits

    def validate_form_inputs(self):

        form = self.request.form

        prefix_text = form.get('kits-prefix-text', None)
        leading_zeros = form.get('kits-leading-zeros', [])
        if not prefix_text:
            msg = u'Prefix text is required.'
            raise ValidationError(msg)

        # TODO: check if leading zeros has only zeros

        try:
            seq_start = int(form.get('seq-start', None))
            kit_count = int(form.get('kit-count', None))
            biospecimen_count = int(form.get('specimen-count', None))
        except:
            raise ValidationError(
                u'Sequence start and all counts must be integers')

        # verify ID sequence start
        if seq_start < 1:
            raise ValidationError(u'Sequence Start must be > 0')

        # verify number of kits
        if kit_count < 1:
            raise ValidationError(u'Kit count must be > 0')

        # verify number of biospecimen per kit
        if biospecimen_count < 1:
            raise ValidationError(u'Number of biospecimens per kit must be > 0')

        # Kit template required
        kit_template_uid = self.form.get('kit_template_uid', None)

        # Stock Item storage (where items will be taken from), is required
        si_storage_uids = form.get('si-storage-uids', '')
        if not si_storage_uids and kit_template_uid:
            raise ValidationError(u'You must select the items storage to use for '
                                  u'the kit assembling.')

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues()]
        for x in range(kit_count):
            id_kit = prefix_text + '-' + str(seq_start + x).zfill(len(leading_zeros) + 1)
            if id_kit in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % id_kit)

        # Check there are enough stock items in stock to create the kits
        if kit_template_uid:
            kit_template = self.bsc(UID=kit_template_uid)[0].getObject()
            for product in kit_template.getProductList():
                items = self.product_stock_items(product['product_uid'])
                items = self.filter_stock_items_by_storage(items)
                quantity = sum([item.getQuantity() for item in items])
                if quantity < int(product['quantity']) * kit_count:
                    raise ValidationError(
                        u"There is insufficient stock items available for "
                        u"product '%s'." % product['product'])

        # Biospecimen storage (where biospecimen items will be stored) is required to be booked
        biospecimen_storage_uids = form.get('biospecimen-storage-uids', '')
        if not biospecimen_storage_uids:
            raise ValidationError(u'You must select the Biospecimen Storage from where the '
                                  u'specimen items will be stored.')

                        # Check that the storage selected has sufficient positions to contain
        # the biospecimen to generate.
        biospecimens_per_kit = int(form.get('specimen-count', None))
        biospecimen_count = kit_count * biospecimens_per_kit
        bio_storages = self.samples_gen.get_biospecimen_storages()
        if all([IManagedStorage.providedBy(storage) for storage in bio_storages]):
            nr_positions = self.samples_gen.count_storage_positions(bio_storages)
            if biospecimen_count > nr_positions:
                raise ValidationError(
                    u"Not enough kit storage positions available.  Please select "
                    u"or create additional storage for kits.")

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg, 'error')
        self.request.response.redirect(self.context.absolute_url() + '/kits')
