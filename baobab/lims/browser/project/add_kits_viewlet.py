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
from baobab.lims.interfaces import IUnmanagedStorage, IStoragePosition, \
    IManagedStorage


class AddKitsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_kits_viewlet.pt")

    # def render(self):
    #     return self.index()

    def render(self):
        if self.request.URL.endswith('kits'):
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
        """ return storages which could store stock items
        """
        si_storages = []
        for uid in self.form['si-storage-uids'].split(','):
            brain = self.bsc(UID=uid)
            if not brain:
                raise ValidationError(u'Bad uid. This should not happen.')
            si_storages.append(brain[0].getObject())

        return si_storages

    def filter_stockitems_by_storage_location(self, items):
        """Return stockitems in the selected storages
        """
        si_storages = self.get_si_storages()
        stockitems = []
        for storage in si_storages:
            if IUnmanagedStorage.providedBy(storage):
                sis = storage.getBackReferences('ItemStorageLocation')
                stockitems += [si for si in sis if si in items]
            elif IManagedStorage.providedBy(storage):
                sis = storage.only_items_of_portal_type('StockItem')
                stockitems += [si for si in sis if si in items]

        return stockitems

    def product_stockitems(self, uid):
        """ stock items of a product uid
        """
        brains = self.bika_setup_catalog(
            portal_type='StockItem',
            getProductUID=uid,
            review_state='available')
        items = [b.getObject() for b in brains]

        return items

    def stockitems_for_template(self, template):
        """ Return stockitems of kit template's products
        """
        stockitems = []
        for product in template.getProductList():
            items = self.product_stockitems(product['product_uid'])
            items = self.filter_stockitems_by_storage_location(items)
            quantity = int(product['quantity'])
            if len(items) < quantity:
                msg = u"There is insufficient stock available for the " \
                    u"product '%s'." % product['product']
                self.form_error(msg)
                raise ValidationError(msg)

            stockitems += items[:quantity]

        return stockitems

    def assign_stockitems_to_kit(self, kit):
        """Find required stock items, remove them from storage, and assign them
        to the kit.
        """
        template = kit.getKitTemplate()
        stockitems = self.stockitems_for_template(template)
        for item in stockitems:
            # Remove from storage and liberate storage position
            location = item.getStorageLocation()
            item.setStorageLocation(None)
            # liberate storage position
            if location.portal_type == 'StoragePosition':
                self.portal_workflow.doActionFor(location, 'liberate')
            # flag stockitem as "used"
            self.portal_workflow.doActionFor(item, 'use')
        # assign all stockitems to the Kit.
        kit.setStockItems(stockitems)

    def update_qtty_products(self, kit):
        """ Update the qtty of products after assigning stock items to
        kit
        """
        template = kit.getKitTemplate()
        # stockitems = self.stockitems_for_template(template)
        products = []
        for item in template.getProductList():
            product = self.bsc(UID=item['product_uid'])[0].getObject()
            products.append(product)
        for product in products:
            stockitems = product.getBackReferences("StockItemProduct")
            qtty = 0
            for si in stockitems:
                if self.wf.getInfoFor(si, 'review_state') == 'available': qtty += 1
            product.setQuantity(qtty)
            product.reindexObject()

    def assign_kit_to_storage(self, kits, storages):
        """ assign position to created kits.
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
        leading_zeros = self.form.get('kits-leading-zeros', None)
        seq_start = int(self.form.get('seq-start', None))
        kit_count = int(self.form.get('kit-count', None))
        kit_template_uid = self.form.get('kit-template-uid', None)
        spec_per_kit = int(self.form.get('specimen-count', None))
        kits = []
        # sample storage
        samples = []
        sample_storage = self.samples_gen.get_biospecimen_storages()

        for x in range(seq_start, seq_start + kit_count):
            id_template = prefix_text + '-' + str(x).zfill(len(leading_zeros))
            title_template = prefix_text + ' ' + str(x).zfill(len(leading_zeros))
            obj = api.content.create(
                container=self.context,
                type='Kit',
                id=id_template,
                title=title_template,
                KitTemplate=kit_template_uid,
                DateCreated=DateTime()
            )
            if kit_template_uid:
                self.assign_stockitems_to_kit(obj)
                self.update_qtty_products(obj)
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
        leading_zeros = form.get('kits-leading-zeros', None)
        if not prefix_text or not leading_zeros:
            msg = u'Prefix text and Leading zeros are both required.'
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
        kit_template_uid = self.form.get('kit-template-uid', None)

        # Stock Item storage (where items will be taken from), is required
        si_storage_uids = form.get('si-storage-uids', '')
        if not si_storage_uids and kit_template_uid:
            raise ValidationError(u'You must select the Storage from where the '
                                  u'stock items will be used for the assembling.')

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues()]
        for x in range(kit_count):
            id_kit = prefix_text + '-' + str(seq_start+ x).zfill(len(leading_zeros))
            if id_kit in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % id_kit)

        # Check there are enough stock items in stock to create the kits
        if kit_template_uid:
            kit_template = self.bsc(UID=kit_template_uid)[0].getObject()
            for item in kit_template.getProductList():
                items = self.product_stockitems(item['product_uid'])
                items = self.filter_stockitems_by_storage_location(items)
                if len(items) < int(item['quantity']) * kit_count:
                    raise ValidationError(
                        u"There is insufficient stock available for " \
                        u"product '%s'." % item['product'])

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
