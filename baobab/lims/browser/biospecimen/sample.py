from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.workflow import doActionFor
from bika.lims.browser import BrowserView
from baobab.lims import bikaMessageFactory as _

from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime

class UpdateBoxes(BrowserView):
    """
    Verify the status of the box when a new biospecimen stored
    """
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        if 'locTitle' in self.request.form:
            location_title = self.request.form['locTitle']
            if location_title:
                bsc = getToolByName(self.context, "portal_catalog")
                brains = bsc.searchResults(portal_type='StoragePos', title=location_title)
                location = brains[0].getObject()
                state = self.context.portal_workflow.getInfoFor(location, 'review_state')
                if state != 'occupied':
                    doActionFor(location, 'occupy')
                    self.context.update_box_status(location)

                prev_location = self.context.getStorageLocation()
                if prev_location and prev_location != location:
                    state = self.context.portal_workflow.getInfoFor(prev_location, 'review_state')
                    if state == 'occupied':
                        doActionFor(prev_location, 'liberate')
                        self.context.update_box_status(prev_location)
            else:
                location = self.context.getStorageLocation()
                if location:
                    doActionFor(location, 'liberate')
                    self.context.update_box_status(location)

        return []


class SampleView(BrowserView):
    """The view of a single sample
    """
    template = ViewPageTemplateFile("templates/sample_view.pt")
    title = _("Biospecimen View")

    def __call__(self):
        context = self.context
        self.absolute_url = context.absolute_url()

        # __Disable the add new menu item__ #
        context.setLocallyAllowedTypes(())

        # __Collect general data__ #
        self.id = context.getId()
        self.title = context.Title()
        self.description = context.Description()
        
        self.icon = self.portal_url + "/++resource++baobab.lims.images/" \
                                    + "biospecimen_big.png"
        parent = context.getField('LinkedSample').get(context)
        self.parent_aliquot = parent and "<a href='%s'>%s</a>" % (
                                     parent.absolute_url(),
                                     parent.Title()) or None

        self.project = "<a href='%s'>%s</a>" % (
            context.aq_parent.absolute_url(),
            context.aq_parent.Title()
        )

        kit = context.getField('Kit').get(context)
        self.kit = kit and "<a href='%s'>%s</a>" % (
                       kit.absolute_url(),
                       kit.Title()) or None

        disease_ontology = context.getField('DiseaseOntology').get(context)
        self.disease_ontology = disease_ontology and "<a href='%s'>%s</a>" % (
            disease_ontology.absolute_url(),
            disease_ontology.Title()) or None

        donor = context.getField('Donor').get(context)
        self.donor = donor and "<a href='%s'>%s</a>" % (
            donor.absolute_url(),
            donor.getSampleDonorID()) or None

        location = context.getField('StorageLocation').get(context)
        self.location = location and "<a href='%s'>%s</a>" % (
                                 location.absolute_url(),
                                 location.Title()) or None

        self.sampling_date = context.getSamplingDate()

        sharing = context.getField('AllowSharing').get(context)
        self.sharing = sharing and "Yes" or "No"

        self.subjectID = context.getField('SubjectID').get(context)
        self.barcode = context.getField('Barcode').get(context)
        self.volume = context.getField('Volume').get(context) + " " + context.getField('Unit').get(context)


        return self.template()


class EditView(BrowserView):
    template = ViewPageTemplateFile('templates/sample_edit.pt')

    def __call__(self):
        request = self.request
        context = self.context

        if 'submitted' in request:

            audit_logger = AuditLogger(self.context, 'Sample')

            from Products.CMFPlone.utils import _createObjectByType
            from bika.lims.utils import tmpID
            pc = getToolByName(context, "portal_catalog")
            folder = pc(portal_type="Project", UID=request.form['Project_uid'])[0].getObject()

            new_sample = False
            if not folder.hasObject(context.getId()):
                sample = _createObjectByType('Sample', folder, tmpID())
                new_sample = True
            else:
                sample = context
                self.perform_sample_audit(sample, request)

            sample.getField('Project').set(sample, request.form['Project_uid'])
            sample.getField('AllowSharing').set(sample, request.form['AllowSharing'])
            sample.getField('Kit').set(sample, request.form['Kit_uid'])
            sample.getField('StorageLocation').set(sample, request.form['StorageLocation_uid'])
            sample.getField('SubjectID').set(sample, request.form['SubjectID'])
            sample.getField('Barcode').set(sample, request.form['Barcode'])
            sample.getField('Volume').set(sample, request.form['Volume'])
            sample.getField('Unit').set(sample, request.form['Unit'])
            sample.getField('LinkedSample').set(sample, request.form['LinkedSample_uid'])

            sample.edit(
                SampleType=request.form['SampleType_uid']
            )
            sample_batch = sample.getField('Batch').get(sample)
            sample.processForm()
            sample.getField('Batch').set(sample, sample_batch)

            obj_url = sample.absolute_url_path()

            if new_sample:
                audit_logger.perform_simple_audit(sample, 'New')
            request.response.redirect(obj_url)

            return

        return self.template()

    def perform_sample_audit(self, sample, request):
        audit_logger = AuditLogger(self.context, 'Sample')
        bc = getToolByName(self.context, 'bika_catalog')
        pc = getToolByName(self.context, "portal_catalog")

        # sample_audit = {}

        audit_logger.perform_reference_audit(sample, 'Kit', sample.getField('Kit').get(sample),
                                             bc, request.form['Kit_uid'])
        audit_logger.perform_reference_audit(sample, 'StorageLocation', sample.getField('StorageLocation').get(sample),
                                             pc, request.form['StorageLocation_uid'])

        sampling_date = request.form['SamplingDate']
        if sampling_date:
            sampling_date = DateTime(getLocalServerTime(sampling_date))
        else:
            sampling_date = None
        if sample.getField('SamplingDate').get(sample) != sampling_date:
            audit_logger.perform_simple_audit(sample, 'SamplingDate', sample.getField('SamplingDate').get(sample),
                                              sampling_date)

        if sample.getField('SubjectID').get(sample) != request.form['SubjectID']:
            audit_logger.perform_simple_audit(sample, 'SubjectID', sample.getField('SubjectID').get(sample),
                                              request.form['SubjectID'])
        if sample.getField('Volume').get(sample) != request.form['Volume']:
            audit_logger.perform_simple_audit(sample, 'Volume', sample.getField('Volume').get(sample), request.form['Volume'])

        if sample.getField('Barcode').get(sample) != request.form['Barcode']:
            audit_logger.perform_simple_audit(sample, 'Barcode', sample.getField('Barcode').get(sample),
                                              request.form['Barcode'])

        if sample.getField('Unit').get(sample) != request.form['Unit']:
            audit_logger.perform_simple_audit(sample, 'Unit', sample.getField('Unit').get(sample), request.form['Unit'])

        audit_logger.perform_reference_audit(sample, 'LinkedSample', sample.getField('LinkedSample').get(sample),
                                             pc, request.form['LinkedSample_uid'])

        if not sample.getField('DateCreated').get(sample):
            audit_logger.perform_simple_audit(sample, 'DateCreated', sample.getField('DateCreated').get(sample), str(DateTime()))

        audit_logger.perform_reference_audit(sample, 'SampleType', sample.getField('SampleType').get(sample),
                                             pc, request.form['SampleType_uid'])




    def get_fields_with_visibility(self, visibility, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        hide_fields = ('DiseaseOntology', 'Donor', 'SamplingDate',
                'SampleCondition', 'SubjectID')
        for fn in hide_fields:
            if fn in schema:
                schema[fn].widget.render_own_label = False,
                schema[fn].widget.visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         }
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:
                fields.append(field)
        return fields
