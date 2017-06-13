from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.schema import ValidationError
from DateTime import DateTime

from baobab.lims.interfaces import IUnmanagedStorage, IStoragePosition, \
    IManagedStorage


class AddKitsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_kits_viewlet.pt")

    def render(self):
        return self.index()


class AddKitsSubmitHandler(BrowserView):
    """
    """

    def __init__(self, context, request):
        super(AddKitsSubmitHandler, self).__init__(context, request)
        self.context = context
        self.request = request
        self.form = request.form

    def __call__(self):

        if "viewlet_submitted" in self.request.form:
            try:
                self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)

            self.context.setConstrainTypesMode(constraintypes.DISABLED)
            kits = self.create_kits()

            msg = u'%s kits assembled.' % len(kits)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def get_kit_storages(self):
        """Take a list of UIDs from the form, and resolve to a list of Storages.
        Accepts ManagedStorage, UnmanagedStorage, or StoragePosition UIDs.
        """
        uc = getToolByName(self.context, 'uid_catalog')
        wf = self.portal_workflow
        kit_storages = []
        form_uids = self.form['kit_storage_uids'].split(',')
        for uid in form_uids:
            brain = uc(UID=uid)[0]
            instance = brain.getObject()
            # last-minute check if this storage is available
            if IUnmanagedStorage.providedBy(instance) \
                    or len(instance.get_free_positions()) > 0:
                kit_storages.append(instance)

        return kit_storages

    @staticmethod
    def count_storage_positions(self, storages):
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
                count += storage.get_free_positions()
            else:
                raise ValidationError("Storage %s is not a valid storage type" %
                                      storage)
        return count

    def get_si_storages(self):
        """ return objects of the selected stock items storages
        """
        uc = getToolByName(self.context, 'uid_catalog')
        si_storages = []
        for uid in self.form['si_storage_uids'].split(','):
            brain = uc(UID=uid)
            if not brain:
                raise ValidationError(u'Bad uid.  Should not happen.')
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

        # if si_storages:
        #     return [item for item in items
        #             if item.getStorageLocation() in si_storages]
        # else:
        #     return items
        return stockitems

    def stockitems_for_template(self, template):
        """ Return stockitems of kit template's products
        """
        stockitems = []
        for product in template.getProductList():
            brains = self.bika_setup_catalog(
                portal_type='StockItem',
                getProductUID=product['product_uid'],
                review_state='available')
            items = [b.getObject() for b in brains]
            items = self.filter_stockitems_by_storage_location(items)
            quantity = int(product['quantity'])
            if len(items) < quantity:
                raise ValidationError(
                    u"There is insufficient stock available for the "
                    u"product '%s'." % product['product'])
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
            item.setDateOpened(DateTime())
            # liberate storage position
            if location.portal_type == 'StoragePosition':
                self.portal_workflow.doActionFor(location, 'liberate')
            # flag stockitem as "used"
            self.portal_workflow.doActionFor(item, 'use')
        # assign all stockitems to the Kit.
        kit.setStockItems(stockitems)

    def assign_kit_to_storage(self, kits, storages):
        """ assign position to created kits.
        """
        wf = getToolByName(self.context, 'portal_workflow')
        for storage in storages:
            if IManagedStorage.providedBy(storage):
                free_positions = storage.get_free_positions()
                if len(kits) <= len(free_positions):
                    for i, kit in enumerate(kits):
                        kit.setStorageLocation(free_positions[i])
                        wf.doActionFor(free_positions[i], 'occupy')
                else:
                    for i, position in enumerate(free_positions):
                        kits[i].setStorageLocation(position)
                        wf.doActionFor(position)
                    kits = kits[len(free_positions):]
            elif IUnmanagedStorage.providedBy(storage):
                # Case of unmanaged storage there is no limit in storage until
                # user manually set the storage as full.
                for kit in kits:
                    kit.setStorageLocation(storage)

    def create_kits(self):
        """Create the new kits
        """
        title_template = self.form.get('titletemplate', None)
        id_template = self.form.get('idtemplate', None)
        seq_start = int(self.form.get('seq_start', None))
        kit_count = int(self.form.get('kit_count', None))
        project_uid = self.form.get('Project_uid', None)
        kit_template_uid = self.form.get('KitTemplate_uid', None)
        kits = []

        kit_storages = self.get_kit_storages()
        if all([IStoragePosition.providedBy(storage) for storage in kit_storages]):
            nr_positions = self.count_storage_positions(kit_storages)
            if kit_count > nr_positions:
                raise ValidationError(
                    u"Not enough kit storage positions available.  Please select "
                    u"or create additional storages for kits.")

        for x in range(seq_start, seq_start + kit_count):
            obj = api.content.create(
                container=self.context,
                type='Kit',
                id=id_template.format(id=x),
                title=title_template.format(id=x),
                Project=project_uid,
                KitTemplate=kit_template_uid,
                DateCreated=DateTime()
            )
            self.assign_stockitems_to_kit(obj)
            self.context.manage_renameObject(obj.id, id_template.format(id=x))
            kits.append(obj)
        # store kits
        self.assign_kit_to_storage(kits, kit_storages)

        return kits

    def validate_form_inputs(self):

        form = self.request.form

        title_template = form.get('titletemplate', None)
        id_template = form.get('idtemplate', None)
        if not (title_template and id_template):
            raise ValidationError(u'ID and Title template are both required.')
        if not ('{id}' in title_template and '{id}' in id_template):
            raise ValidationError(u'ID and Title templates must contain {id} '
                                  u'for ID sequence substitution')

        try:
            seq_start = int(form.get('seq_start', None))
            kit_count = int(form.get('kit_count', None))
        except:
            raise ValidationError(
                u'Sequence start and all counts must be integers')

        # verify ID sequence start
        if seq_start < 1:
            raise ValidationError(u'Sequence Start may not be < 1')

        # verify number of kits
        if kit_count < 1:
            raise ValidationError(u'Kit count must not be < 1')

        # KIT storage destination is required field.
        kit_storage_uids = form.get('kit_storage_uids', '')
        if not kit_storage_uids:
            raise ValidationError(u'You must select the Storage where the kit '
                                  u'items will be stored.')

        # Stock Item storage (where items will be taken from) is required
        si_storage_uids = form.get('si_storage_uids', '')
        if not si_storage_uids:
            raise ValidationError(u'You must select the Storage where the '
                                  u'stock items will be taken from.')

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues()]
        for x in range(kit_count):
            check = id_template.format(id=seq_start + x)
            if check in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % check)

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())
