from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from Products.CMFCore.utils import getToolByName
from zope.schema import ValidationError
from DateTime import DateTime

from bika.sanbi.interfaces import IManagedStorage
from bika.lims.workflow import doActionFor
from bika.sanbi.browser.project import get_storage_objects, count_storage_positions, objects_between_two_uids, \
    assign_items_to_storages, create_sample, create_samplepartition
from bika.sanbi.interfaces import IBiospecimen


class AddAliquotsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_aliquots_viewlet.pt")

    def biospecimens(self):
        """ Return samples providing IBiospecimen of the current project
        """
        items = []
        w_tool = getToolByName(self.context, 'portal_workflow')
        samples = self.context.objectValues('Sample')
        for sample in samples:
            if IBiospecimen.providedBy(sample):
                st1 = w_tool.getStatusOf("bika_sample_workflow", sample)
                st2 = w_tool.getStatusOf("bika_cancellation_workflow", sample)
                if st1.get('review_state', None) == 'sample_received' and \
                                st2.get('cancellation_state', None) == 'active':
                    items.append({'uid': sample.UID(), 'title': sample.Title()})
        items.sort(lambda x, y: cmp(x['title'], y['title']))

        return items

    def render(self):
        if self.request.URL.endswith('aliquots'):
            return self.index()
        else:
            return ''


class AddAliquotsSubmitHandler(BrowserView):
    """Handle post form submission
    """
    def __init__(self, context, request):
        super(AddAliquotsSubmitHandler, self).__init__(context, request)
        self.context = context
        self.request = request
        self.form = self.request.form

    def __call__(self):

        if "viewlet_submitted" in self.request.form:
            data = {}
            try:
                data = self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)

            # Validation is complete, now set local variables from form inputs.
            aliquots = []
            j = 0
            workflow_enabled = self.context.bika_setup.getSamplingWorkflowEnabled()
            for x in range(data['seq_start'], data['seq_start'] + data['count']):
                aliquot = create_sample(self.context, self.request, data, j, x)
                partition = create_samplepartition(aliquot, {'services': [], 'part_id': aliquot.getId() + "-P"})
                if not workflow_enabled:
                    doActionFor(aliquot, 'sample_due')
                    doActionFor(partition, 'sample_due')
                # aliquot.setLinkedSample(data['biospecimens'][j].UID())
                aliquot.reindexObject()
                if (x-data['seq_start']+1) % data['aliquot_count'] == 0 and (x-data['seq_start']+1) != 0:
                    j += 1
                aliquots.append(aliquot)

            # store the created biospecimens
            assign_items_to_storages(self.context, aliquots, data['storages'])

            msg = u'%s Aliquots created.' % len(aliquots)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url() + '/aliquots')

    def validate_form_inputs(self):
        """Validate form inputs
        """
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

        uid_1 = form.get('first_biosepcimen_limit', None)
        uid_2 = form.get('last_biospecimen_limit', None)
        if not uid_1 or not uid_2:
            raise ValidationError(u'Kits range is required. Or project select has no kits!')

        biospecimens = objects_between_two_uids(self.context, uid_1, uid_2,
                                                'Sample', 'bika_sample_workflow',
                                                'bika_cancellation_workflow', 'sample_received')

        bio_count = len(biospecimens)
        aliquot_count = int(form.get('aliquot_count', None))
        count = bio_count * aliquot_count

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues('Aliquot')]
        for x in range(count):
            check = id_template.format(id=seq_start + x)
            if check in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % check)

        # Check that the storages selected has sufficient positions to contain
        # the biospecimen to generate.
        storage_uids = self.form['aliquot_storage_uids'].split(',')
        aliquot_storages = get_storage_objects(self.context, storage_uids)
        if all([IManagedStorage.providedBy(storage) for storage in aliquot_storages]):
            nr_positions = count_storage_positions(aliquot_storages)
            if aliquot_count > nr_positions:
                raise ValidationError(
                    u"Not enough kit storage positions available.  Please select "
                    u"or create additional storages for kits.")
        return {
            'title_template': title_template,
            'id_template': id_template,
            'seq_start': seq_start,
            'first_bio_limit': uid_1,
            'last_bio_limit': uid_2,
            'biospecimens': biospecimens,
            'count': count,
            'aliquot_count': aliquot_count,
            'storages': aliquot_storages
        }

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url() + '/aliquots')
