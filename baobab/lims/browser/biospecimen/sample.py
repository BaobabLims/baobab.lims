from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.workflow import doActionFor
from bika.lims.browser import BrowserView
from baobab.lims import bikaMessageFactory as _


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

        patient = context.getField('Patient').get(context)
        self.patient = patient and "<a href='%s'>%s</a>" % (
            patient.absolute_url(),
            patient.getPatientID()) or None

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
            from Products.CMFPlone.utils import _createObjectByType
            from bika.lims.utils import tmpID
            pc = getToolByName(context, "portal_catalog")
            folder = pc(portal_type="Project", UID=request.form['Project_uid'])[0].getObject()
            if not folder.hasObject(context.getId()):
                sample = _createObjectByType('Sample', folder, tmpID())
            else:
                sample = context
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

            sample.processForm()

            obj_url = sample.absolute_url_path()
            request.response.redirect(obj_url)
            return

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