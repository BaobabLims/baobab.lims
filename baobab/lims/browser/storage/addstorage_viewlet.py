from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zExceptions import BadRequest
from zope.dottedname.resolve import resolve
from zope.interface import alsoProvides
from zope.schema import ValidationError
from baobab.lims.browser.storage import getStorageTypes


class AddStorageViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/addstorage_viewlet.pt")
    add_managed_pt = ViewPageTemplateFile("templates/add_managed.pt")
    add_unmanaged_pt = ViewPageTemplateFile("templates/add_unmanaged.pt")
    add_units_pt = ViewPageTemplateFile("templates/add_units.pt")

    def storage_types(self):
        """Return UI-friendly formatted version of getStorageTypes() output
        """
        return getStorageTypes()

    def dlclass(self):
        """We want to automatically flag the viewlet expanded if there
        are no storage objects at this location.
        """
        if self.context.objectValues():
            return "collapsible collapsedOnLoad"
        else:
            return "collapsible"

    def render(self):
        return self.index()

    def addstorage_viewlet_body(self):
        return self.viewlet_body_pt()

    def add_units(self):
        return self.add_units_pt()

    def add_managed(self):
        return self.add_managed_pt(storage_types=self.storage_types())

    def add_unmanaged(self):
        return self.add_unmanaged_pt(storage_types=self.storage_types())

    def show_managed(self):
        if self.request.URL.endswith('/storage') \
                or self.request.URL.endswith('/storage/view'):
            return False
        return True

    def show_unmanaged(self):
        if self.request.URL.endswith('/storage') \
                or self.request.URL.endswith('/storage/view'):
            return False
        return True

    def show_units(self):
        if self.request.URL.endswith('/fullboxes'):
            return False
        return True

    def show_department(self):
        if self.context.portal_type == 'StorageUnit' and \
                self.context.getDepartment():
            return False
        return True

class AddStorageSubmit(BrowserView):
    """
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):

        form = self.request.form

        if 'addstorage_managed_submitted' in form:
            return AddManagedStorage(self.context, self.request)()
        elif 'addstorage_unmanaged_submitted' in form:
            return AddUnmanagedStorage(self.context, self.request)()
        elif 'add_units_submitted' in form:
            return AddStorageUnits(self.context, self.request)()


class Storage(BrowserView):
    def __init__(self, context, request):
        super(Storage, self).__init__(context, request)
        self.context = context
        self.request = request

    def get_sequence(self, start, nr_items):

        # Always nr_items must be int > 0.
        try:
            nr_items = int(nr_items)
        except ValueError:
            nr_items = 1

        # plain numbers:
        try:
            start = int(start)
            sequence = range(start, start + nr_items)
        except ValueError as e:
            self.form_error(
                "Start sequence and number of items should be integers.")
            raise ValidationError

        return sequence

    def inc_str(self, str):
        ords = [ord(x) for x in str]
        inced_ords = self.inc_ords(ords)
        return ''.join([chr(x) for x in inced_ords])

    def storage_types(self):
        """Return UI-friendly formatted version of getStorageTypes() output
        """
        return getStorageTypes()

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg, 'error')
        self.request.response.redirect(self.context.absolute_url())


class AddStorageUnits(Storage):
    def __init__(self, context, request):
        super(AddStorageUnits, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        try:
            self.validate_form_inputs()
        except ValidationError as e:
            self.form_error(e.message)
            return

        units = self.create_units()

        msg = u'%s Storage units created.' % len(units)
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())

    def create_units(self):
        """Create the new storage unit items from form values.
        """
        form = self.request.form
        bsc = getToolByName(self, 'bika_setup_catalog')
        # titles
        prefix_text = form.get('units-prefix-text', None)
        leading_zeros = form.get('units-leading-zeros', [])
        # schema
        unit_type = form.get('units_type_uid', None)
        temperature = ''
        if unit_type:
            brains = bsc(portal_type='StorageType', UID=unit_type)
            temperature = brains[0].getObject().getTemperature()
        if not temperature:
            if self.context.portal_type == 'StorageUnit':
                temperature = self.context.getTemperature()
        address = form.get('units_address', None)  # schema
        department = form.get('units_department_uid', None)
        if not department and self.context.portal_type == 'StorageUnit':
            department = self.context.getDepartment()

        start = form['units_start']
        nr_items = int(form['units_nr_items'])

        units = []
        for x in self.get_sequence(start, nr_items):
            id_template = prefix_text + '-' + str(x).zfill(len(leading_zeros) + 1)
            title_template = prefix_text + ' ' + str(x).zfill(len(leading_zeros) + 1)
            try:
                instance = api.content.create(
                    container=self.context,
                    type="StorageUnit",
                    id=id_template,
                    title=title_template)
            except BadRequest as e:
                msg = e.message
                self.form_error(msg)
                self.request.response.redirect(self.context.absolute_url())
                return []

            # schema
            self.set_inputs_into_schema(
                instance,
                temperature,
                department,
                address,
                unit_type
            )

            # self.context.manage_renameObject(instance.id, id_template)

            units.append(instance)

        return units

    def validate_form_inputs(self):
        form = self.request.form
        # Prefix and Leading zeros
        prefix_text = self.request.form.get('units-prefix-text', None)
        leading_zeros = self.request.form.get('units-leading-zeros', [])
        if not prefix_text:
            msg = u'Prefix text is required.'
            raise ValidationError(msg)

        # TODO: check if leading zeros has only zeros

        # check for valid integer values
        try:
            nr_items = int(form['units_nr_items'])
        except:
            msg = u'Item count must be an integer.'
            raise ValidationError(msg)
        if nr_items < 1:
            msg = u'Item count must be > 0.'
            raise ValidationError(msg)

        # Check that none of the IDs conflict with existing items
        start = form['units_start']
        nr_items = int(form['units_nr_items'])
        ids = [x.id for x in self.context.objectValues()]
        for x in self.get_sequence(start, nr_items):
            id_unit = prefix_text + '-' + str(x).zfill(len(leading_zeros) + 1)
            if  id_unit in ids:
                msg = u'The ID %s already exists.' % id_unit
                raise ValidationError(msg)

    def set_inputs_into_schema(
            self, instance, temperature, department, address, unit_type):
        # Set field values across each object if possible
        schema = instance.Schema()
        if temperature and 'Temperature' in schema:
            instance.Schema()['Temperature'].set(instance, temperature)
        if department and 'Department' in schema:
            instance.Schema()['Department'].set(instance, department)
        if address and 'Address' in schema:
            instance.Schema()['Address'].set(instance, address)
        if unit_type and 'UnitType' in schema:
            instance.Schema()['UnitType'].set(instance, unit_type)


class AddManagedStorage(Storage):
    def __init__(self, context, request):
        super(AddManagedStorage, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        try:
            self.validate_form_inputs()
        except ValidationError as e:
            self.form_error(e.message)
            return

        form = self.request.form
        storages = self.create_managed_storages()

        msg = u'%s Managed storages created (%s to %s)' % \
              (len(storages), storages[0].id, storages[-1].id)
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())

    def create_managed_storages(self):
        """Create the new managed storages from form values.
        """
        form = self.request.form
        # titles
        prefix_text = form.get('managed-prefix-text', None)
        leading_zeros = form.get('managed-leading-zeros', [])
        # schema
        # temperature = form.get('managed-temperature', '')

        start = form['managed-start']
        nr_items = int(form['managed-nr-items'])

        nr_positions = int(form.get('managed-positions', 0))

        storage_types = form.get('managed-storage-types', [])
        if isinstance(storage_types, basestring):
            storage_types = [storage_types]

        XAxis = form.get('managed-x', nr_positions)
        YAxis = form.get('managed-y', 0)

        storages = []
        for x in self.get_sequence(start, nr_items):
            id_template = prefix_text + '-' + str(x).zfill(len(leading_zeros) + 1)
            title_template = prefix_text + ' ' + str(x).zfill(len(leading_zeros) + 1)
            storage = api.content.create(
                container=self.context,
                type="ManagedStorage",
                id=id_template,
                title=title_template,
                XAxis=int(XAxis),
                YAxis=int(YAxis)
            )

            # storage types are set on this managed storage:
            self.set_storage_types(storage, storage_types)
            storage.reindexObject()
            # Create storage positions
            for p in range(1, nr_positions + 1):
                title = storage.getHierarchy() + ".{id}".format(id=str(p).zfill(len(str(nr_positions))))
                pos = api.content.create(
                    container=storage,
                    type="StoragePosition",
                    id="{id}".format(id=p),  # XXX hardcoded pos title and id
                    # title=storage.getHierarchy() + ".{id}".format(id=p))
                    title=title)
                # storage types are set on each pos inside the storage too.
                self.set_storage_types(pos, storage_types)
                pos.reindexObject()

            storages.append(storage)

        return storages

    def set_storage_types(self, instance, storage_types):
        # Set field values across each object if possible
        schema = instance.Schema()
        if storage_types and 'StorageTypes' in schema:
            instance.Schema()['StorageTypes'].set(instance, storage_types)
        self.provide_storagetype_interfaces(instance, storage_types)

    def provide_storagetype_interfaces(self, instance, storage_types):
        """Assign any selected storage type interfaces to this location.
        """
        for storage_type in storage_types:
            inter = resolve(storage_type)
            alsoProvides(instance, inter)

    def validate_form_inputs(self):
        form = self.request.form
        # Prefix and Leading zeros
        prefix_text = self.request.form.get('managed-prefix-text', None)
        leading_zeros = self.request.form.get('managed-leading-zeros', [])
        if not prefix_text:
            msg = u'Prefix text is required.'
            raise ValidationError(msg)

        # TODO: check if leading zeros has only zeros

        # check for valid integer values
        try:
            nr_items = int(form.get('managed-nr-items', None))
            fnrp = form.get('managed-positions', 0)
            if not fnrp:
                fnrp = 0
            nr_positions = int(fnrp)
        except:
            msg = u'Item and position count must be numbers'
            raise ValidationError(msg)
        if nr_items < 1:
            msg = u'Item count must be > 0.'

            raise ValidationError(msg)
        if nr_positions < 1:
            msg = u'Position count must be > 1.'
            raise ValidationError(msg)

        # verify storage_type interface selection
        storage_types = form.get('managed-storage-types', [])
        if any([storage_types, nr_positions]) \
                and not all([storage_types, nr_positions]):
            raise ValidationError(
                u'To create managed storage, at least one storage type must be '
                u'selected, and the number of storage positions must be > 0.')

        # Check that none of the IDs conflict with existing items
        start = form['managed-start']
        nr_items = int(form['managed-nr-items'])
        ids = [x.id for x in self.context.objectValues()]
        for x in self.get_sequence(start, nr_items):
            id_storage = prefix_text + '-' + str(x).zfill(len(leading_zeros) + 1)
            if id_storage in ids:
                msg = u'The ID %s already exists.' % id_storage
                raise ValidationError(msg)


class AddUnmanagedStorage(Storage):
    def __init__(self, context, request):
        super(AddUnmanagedStorage, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        try:
            self.validate_form_inputs()
        except ValidationError as e:
            self.form_error(e.message)
            return

        form = self.request.form
        storages = self.create_unmanaged_storages()

        msg = u'%s Unmanaged storages created (%s to %s)' % \
              (len(storages), storages[0].id, storages[-1].id)
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())

    def create_unmanaged_storages(self):
        """Create the new unmanaged storages from form values.
        """
        form = self.request.form
        # titles
        prefix_text = form.get('unmanaged-prefix-text', None)
        leading_zeros = form.get('unmanaged-leading-zeros', [])
        # schema
        # temperature = form.get('unmanaged-temperature', '')

        start = form['unmanaged-start']
        nr_items = int(form['unmanaged-nr-items'])

        storage_types = form.get('umanaged-storage-types', [])
        if isinstance(storage_types, basestring):
            storage_types = [storage_types]

        storages = []
        for x in self.get_sequence(start, nr_items):
            id_template = prefix_text + '-' + str(x).zfill(len(leading_zeros) + 1)
            title_template = prefix_text + ' ' + str(x).zfill(len(leading_zeros) + 1)
            instance = api.content.create(
                container=self.context,
                type="UnmanagedStorage",
                id=id_template,
            )

            # change title to hierarchy plus id
            instance.setTitle(instance.getHierarchy())

            if instance.id != id_template:
                self.context.manage_renameObject(
                    instance.id, id_template)

            # storage types are set on this managed storage:
            self.set_storage_types(instance, storage_types)
            instance.reindexObject()

            storages.append(instance)
        return storages

    def set_storage_types(self, instance, storage_types):
        # Set field values across each object if possible

        schema = instance.Schema()
        if storage_types and 'StorageTypes' in schema:
            instance.Schema()['StorageTypes'].set(instance, storage_types)
        self.provide_storagetype_interfaces(instance, storage_types)

    def provide_storagetype_interfaces(self, instance, storage_types):
        """Assign any selected storage type interfaces to the storage.
        """
        for storage_type in storage_types:
            inter = resolve(storage_type)
            alsoProvides(instance, inter)

    def validate_form_inputs(self):
        form = self.request.form
        # Prefix and Leading zeros
        prefix_text = self.request.form.get('unmanaged-prefix-text', None)
        leading_zeros = self.request.form.get('unmanaged-leading-zeros', [])
        if not prefix_text:
            msg = u'Prefix text is required.'
            raise ValidationError(msg)

        # TODO: check if leading zeros has only zeros

        # check for valid integer values
        try:
            nr_items = int(self.request.form.get('unmanaged-nr-items', None))
        except:
            msg = u'Item count must be an integer.'
            raise ValidationError(msg)

        if nr_items < 1:
            msg = u'Item count must be > 0'
            raise ValidationError(msg)

        # Check that none of the IDs conflict with existing items
        start = int(form['unmanaged-start'])
        nr_items = int(form['unmanaged-nr-items'])
        ids = [x.id for x in self.context.objectValues()]
        for x in self.get_sequence(start, nr_items):
            id_storage = prefix_text + '-' + str(x).zfill(len(leading_zeros) + 1)
            if id_storage in ids:
                msg = u'The ID %s already exists.' % x
                raise ValidationError(msg)

        # verify storage_type interface selection
        storage_types = form.get('umanaged-storage-types', [])
        if not storage_types:
            raise ValidationError(
                u'To create managed storage, at least one storage type must be selected.')
