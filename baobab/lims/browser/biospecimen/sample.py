from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.workflow import doActionFor
from bika.lims.browser import BrowserView
from bika.lims.browser.sample import SampleEdit as SE


class SampleEdit(SE):
    """This overrides the edit and view of sample.
    """

    def __init__(self, context, request):
        SE.__init__(self, context, request)
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/biospecimen_big.png"
        self.allow_edit = True

    def __call__(self):
        SE.__call__(self)
        return self.template()


class SampleView(SampleEdit):
    """The view of a single sample
    """
    def __call__(self):
        self.allow_edit = False
        return SampleEdit.__call__(self)


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
                bsc = getToolByName(self.context, "bika_setup_catalog")
                brains = bsc.searchResults(title=location_title)
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

            obj_url = context.absolute_url_path()
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