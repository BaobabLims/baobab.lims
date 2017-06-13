from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from zope.schema import ValidationError
from Products.CMFCore.utils import getToolByName

from baobab.lims.interfaces import IUnmanagedStorage, IManagedStorage
from bika.lims.workflow import doActionFor
from baobab.lims.browser.project import create_sample, create_samplepartition


class AddBiospecimensViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_biospecimens_viewlet.pt")

    def kits(self):
        """ Return only project's kits with status generated and active
        """
        items = []
        w_tool = getToolByName(self.context, 'portal_workflow')
        kits = self.context.objectValues('Kit')
        for kit in kits:
            st1 = w_tool.getStatusOf("bika_kit_assembly_workflow", kit)
            st2 = w_tool.getStatusOf("bika_inactive_workflow", kit)
            if st1.get('review_state', None) == 'received' and \
                            st2.get('inactive_state', None) == 'active':
                items.append({'uid':kit.UID(), 'title':kit.Title()})
        items.sort(lambda x, y: cmp(x['title'], y['title']))

        return items

    def render(self):
        if self.request.URL.endswith('biospecimens'):
            return self.index()
        else:
            return ''


class AddBiospecimensSubmitHandler(BrowserView):
    """
    """

    def __init__(self, context, request):
        super(AddBiospecimensSubmitHandler, self).__init__(context, request)
        self.context = context
        self.request = request
        self.form = request.form

    def assign_biospecimens_to_storages(self, biospecimens, storages):
        """ Assign positions to biospecimens inside storages
        """
        wf = getToolByName(self.context, 'portal_workflow')
        for storage in storages:
            if IManagedStorage.providedBy(storage):
                free_positions = storage.get_free_positions()
                if len(biospecimens) <= len(free_positions):
                    for i, biospecimen in enumerate(biospecimens):
                        biospecimen.setStorageLocation(free_positions[i])
                        wf.doActionFor(free_positions[i], 'occupy')
                else:
                    for i, position in enumerate(free_positions):
                        biospecimens[i].setStorageLocation(position)
                        wf.doActionFor(position, 'occupy')
                    biospecimens = biospecimens[len(free_positions):]
            elif IUnmanagedStorage.providedBy(storage):
                # Case of unmanaged storage there is no limit in storage until
                # user manually set the storage as full.
                for biospecimen in biospecimens:
                    biospecimen.setStorageLocation(storage)

    def __call__(self):
        if "viewlet_submitted" in self.request.form:
            data = {}
            try:
                data = self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)

            # Validation is complete, now set local variables from form inputs.
            biospecimens = []
            j = 0
            if data:
                workflow_enabled = self.context.bika_setup.getSamplingWorkflowEnabled()
                for x in range(data['seq_start'], data['seq_start'] + data['biospecimen_count']):
                    sample = create_sample(self.context, self.request, data, j, x)
                    partition = create_samplepartition(sample, {'services':[], 'part_id': sample.getId() + "-P"})
                    if not workflow_enabled:
                        doActionFor(sample, 'sample_due')
                        doActionFor(partition, 'sample_due')
                    sample.reindexObject()
                    if (x-data['seq_start']+1) % data['biospecimen_per_kit'] == 0 and (x-data['seq_start']+1) != 0:
                        j += 1
                    biospecimens.append(sample)

                #store the created biospecimens
                self.assign_biospecimens_to_storages(biospecimens, data['storages'])

                msg = u'%s Biospecimens created.' % len(biospecimens)
                self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url() + '/biospecimens')

    def kits_between_limits(self, first_limit_uid, last_limit_uid):
        """Retrieve kits between the two limits
        """
        w_tool = getToolByName(self.context, 'portal_workflow')
        uc = getToolByName(self.context, 'uid_catalog')
        first_kit_id = uc(UID=first_limit_uid)[0].id
        last_kit_id = uc(UID=last_limit_uid)[0].id
        p_kits = self.context.objectValues('Kit')
        # Filter kits by workflow state active
        kits = []
        for kit in p_kits:
            st1 = w_tool.getStatusOf("bika_kit_assembly_workflow", kit)
            st2 = w_tool.getStatusOf("bika_inactive_workflow", kit)
            if st1.get('review_state', None) == 'received' and \
                    st2.get('inactive_state', None) == 'active' and \
                        first_kit_id <= kit.getId() <= last_kit_id:
                kits.append(kit)

        return kits

    def get_biospecimen_storages(self):
        """Take a list of UIDs from the form, and resolve to a list of Storages.
        Accepts ManagedStorage, UnmanagedStorage, or StoragePosition UIDs.
        """
        uc = getToolByName(self.context, 'uid_catalog')
        bio_storages = []
        form_uids = self.form['biospecimen_storage_uids'].split(',')
        for uid in form_uids:
            brain = uc(UID=uid)[0]
            instance = brain.getObject()
            if IUnmanagedStorage.providedBy(instance) \
                    or len(instance.get_free_positions()) > 0:
                bio_storages.append(instance)

        return bio_storages

    @staticmethod
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
        except:
            raise ValidationError(
                u'Sequence start and all counts must be integers')

        first_kit_limit = form.get('first_kit_limit', None)
        last_kit_limit = form.get('last_kit_limit', None)
        if not first_kit_limit or not last_kit_limit:
            raise ValidationError(u'Kits range is required. Or project select has no kits!')

        kits = self.kits_between_limits(first_kit_limit, last_kit_limit)
        count = len(kits)
        biospecimen_per_kit = int(form.get('biospecimen_per_kit', None))
        biospecimen_count = count * biospecimen_per_kit

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues()]
        for x in range(biospecimen_count):
            check = id_template.format(id=seq_start + x)
            if check in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % check)

        # Check that the storages selected has sufficient positions to contain
        # the biospecimen to generate.
        bio_storages = self.get_biospecimen_storages()
        if all([IManagedStorage.providedBy(storage) for storage in bio_storages]):
            nr_positions = self.count_storage_positions(bio_storages)
            if biospecimen_count > nr_positions:
                raise ValidationError(
                    u"Not enough kit storage positions available.  Please select "
                    u"or create additional storages for kits.")

        return {
            'title_template': title_template,
            'id_template': id_template,
            'seq_start': seq_start,
            'first_kit_limit': first_kit_limit,
            'last_kit_limit': last_kit_limit,
            'kits': kits,
            'biospecimen_per_kit': biospecimen_per_kit,
            'biospecimen_count': biospecimen_count,
            'storages': bio_storages
        }

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url() + '/biospecimens')
