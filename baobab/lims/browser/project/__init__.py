# Imports
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from zope.interface import alsoProvides
from zope.schema import ValidationError
from DateTime import DateTime

from baobab.lims.interfaces import IManagedStorage, IUnmanagedStorage
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from baobab.lims.interfaces import IBiospecimen
from project import ProjectView


def get_first_sampletype(context):
    """
    This function is used to set the first sample type to a sample created using kit form. We do this
    to allow idserver to generate an id to the sample created.
    :param context:
    :return:
    """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    bsc = getToolByName(context, 'bika_setup_catalog')
    results = bsc.unrestrictedSearchResults({'portal_type': 'SampleType'})
    return portal.unrestrictedTraverse(results[0].getPath()) if len(results) else None


def get_storage_objects(context, storage_uids):
    """Take a list of UIDs from the form, and resolve to a list of Storages.
    Accepts ManagedStorage, UnmanagedStorage, or StoragePosition UIDs.
    """
    uc = getToolByName(context, 'uid_catalog')
    bio_storages = []
    for uid in storage_uids:
        brain = uc(UID=uid)[0]
        instance = brain.getObject()
        if IUnmanagedStorage.providedBy(instance) \
                or len(instance.get_free_positions()) > 0:
            bio_storages.append(instance)

    return bio_storages


def count_storage_positions(storages):
    """"Return the number of items that can be stored in storages.
    This method is called in case all the storages are of type Managed.
    """
    count = 0
    for storage in storages:
        # If storage is a ManagedStorage, increment count for each
        # available StoragePosition
        if IManagedStorage.providedBy(storage):
            count += storage.getFreePositions()
        else:
            raise ValidationError("Storage %s is not a valid storage type" %
                                  storage)
    return count


def objects_between_two_uids(context, uid_1, uid_2, portal_type, wf_1, wf_2, state):
    """Retrieve the objects of type portal_type between two ordered objects
    using their uids.
    """
    w_tool = getToolByName(context, 'portal_workflow')
    uc = getToolByName(context, 'uid_catalog')
    first_id = uc(UID=uid_1)[0].id
    last_id = uc(UID=uid_2)[0].id
    objects = context.objectValues(portal_type)
    # Filter objects by workflow state active
    items = []
    for obj in objects:
        if IBiospecimen.providedBy(obj):
            st1 = w_tool.getStatusOf(wf_1, obj)
            st2 = w_tool.getStatusOf(wf_2, obj)
            if st1.get('review_state', None) == state and \
                            st2.get('cancellation_state', None) == 'active' and \
                                    first_id <= obj.getId() <= last_id:
                items.append(obj)

    return items


def assign_items_to_storages(context, items, storages):
    """ store items inside selected storages
    """
    wf = getToolByName(context, 'portal_workflow')
    for storage in storages:
        if IManagedStorage.providedBy(storage):
            free_positions = storage.get_free_positions()
            if len(items) <= len(free_positions):
                for i, item in enumerate(items):
                    item.setStorageLocation(free_positions[i])
                    wf.doActionFor(free_positions[i], 'occupy')
            else:
                for i, position in enumerate(free_positions):
                    items[i].setStorageLocation(position)
                    wf.doActionFor(position, 'occupy')
                items = items[len(free_positions):]
        elif IUnmanagedStorage.providedBy(storage):
            # Case of unmanaged storage there is no limit in storage until
            # user manually set the storage as full.
            for item in items:
                item.setStorageLocation(storage)


def create_sample(context, request, values, j, x):
    """Create sample as biospecimen or aliquot
    """
    # Retrieve the required tools
    uc = getToolByName(context, 'uid_catalog')
    # Determine if the sampling workflow is enabled
    workflow_enabled = context.bika_setup.getSamplingWorkflowEnabled()
    # Create sample or refer to existing for secondary analysis request
    sample = _createObjectByType('Sample', context, tmpID())
    # Update the created sample with indicated values
    sample.processForm(REQUEST=request, values=values)
    if 'datesampled' in values:
        sample.setDateSampled(values['datesampled'])
    else:
        sample.setDateSampled(DateTime())
    if 'datereceived' in values:
        sample.setDateReceived(values['datereceived'])
    else:
        sample.setDateReceived(DateTime())
    if 'datesampling' in values:
        sample.setSamplingDate(values['datesampling'])
    else:
        sample.setSamplingDate(DateTime())
    if 'datecreated' in values:
        field = sample.getField('DateCreated')
        field.set(sample, values['datecreated'])
    else:
        field = sample.getField('DateCreated')
        field.set(sample, DateTime())
    # Specifically set the storage location
    if 'StorageLocation' in values:
        sample.setStorageLocation(values['StorageLocation'])
    if 'kits' in values:
        field = sample.getField('Kit')
        field.set(sample, values['kits'][j].UID())
        alsoProvides(sample, IBiospecimen)
    if 'biospecimens' in values:
        field = sample.getField('LinkedSample')
        field.set(sample, values['biospecimens'][j].UID())
        # sample.setLinkedSample(values['biospecimens'][j].UID())
        # alsoProvides(sample, IAliquot)
    context.manage_renameObject(sample.id, values['id_template'].format(id=x), )
    # Perform the appropriate workflow action
    workflow_action = 'sampling_workflow' if workflow_enabled \
        else 'no_sampling_workflow'
    doActionFor(sample, workflow_action)
    # Set the SampleID
    sample.edit(SampleID=sample.getId())
    # Return the newly created sample
    return sample


def create_samplepartition(context, data):
    """ Create partition object for sample(context)
    """
    partition = _createObjectByType('SamplePartition', context, data['part_id'])
    partition.unmarkCreationFlag()
    partition.reindexObject()

    return partition


def template_stock_items(template, bsc, pc, workflow, storage_uids):
    """ Return stock-items of kit template's products
    """
    stock_items = []
    for product in template.getProductList():
        items = product_stock_items(product['product_uid'], bsc)
        items = filter_stock_items_by_storage(items, pc, storage_uids)
        quantity_product = int(product['quantity'])
        quantity_stock_items = sum([item.getQuantity() for item in items])
        if quantity_stock_items < quantity_product:
            msg = u"There is insufficient stock available for the " \
                u"product '%s'." % product['product']
            raise ValueError(msg)

        for item in items:
            if item.getQuantity() <= quantity_product:
                quantity_product -= item.getQuantity()
                item.setQuantity(0)
                workflow.doActionFor(item, 'use')
            else:
                item.setQuantity(item.getQuantity() - quantity_product)
                quantity_product = 0

            stock_items.append(item)

            if quantity_product == 0:
                break

    return stock_items


def product_stock_items(uid, bsc):
    """ stock items of a product uid
    """
    brains = bsc(
        portal_type='StockItem',
        getProductUID=uid,
        review_state='available')
    items = [b.getObject() for b in brains]

    return items


def filter_stock_items_by_storage(items, portal_catalog, storage_uids):
    """Return stock-items in the selected storage
    """
    si_storage = get_si_storages(storage_uids, portal_catalog)
    stock_items = []
    for storage in si_storage:
        if IUnmanagedStorage.providedBy(storage):
            sis = storage.getBackReferences('ItemStorageLocation')
            stock_items += [si for si in sis if si in items]
        elif IManagedStorage.providedBy(storage):
            sis = storage.only_items_of_portal_type('StockItem')
            stock_items += [si for si in sis if si in items]

    return stock_items


def get_si_storages(storage_uids, portal_catalog):
    """ return storage which could store stock-items
    """
    si_storage = []
    for uid in storage_uids:
        brain = portal_catalog(UID=uid)
        if not brain:
            raise ValidationError(u'Bad uid. This should not happen.')
        si_storage.append(brain[0].getObject())

    return si_storage


def update_quantity_products(kit, bika_setup_catalog):
    """ Update the products quantity after assigning stock-items to kit
    """
    template = kit.getKitTemplate()
    products = []
    for item in template.getProductList():
        product = bika_setup_catalog(UID=item['product_uid'])[0].getObject()
        products.append(product)
    for product in products:
        stock_items = product.getBackReferences("StockItemProduct")
        quantity = sum([item.getQuantity() for item in stock_items])
        product.setQuantity(quantity)
        product.reindexObject()



