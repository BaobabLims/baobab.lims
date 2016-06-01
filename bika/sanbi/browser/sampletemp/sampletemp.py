from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.lib import constraintypes
from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView
import json


class SampletempEdit(BrowserView):
    template = ViewPageTemplateFile('templates/sampletemp_edit.pt')
    title = _("Sample Add/Edit")

    def __init__(self, context, request):
        self.context = context
        self.request = request

        super(SampletempEdit, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.sanbi.images/sample_big.png"

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        form = self.request.form
        if 'submit' in request:
            context.setConstrainTypesMode(constraintypes.DISABLED)

            # If we edit sample with empty location we have edit location too and make it's state free.
            if not form.get('StorageLocation', ''):
                wftool = self.context.portal_workflow
                location = self.context.getStorageLocation()
                if location:
                    state = wftool.getInfoFor(location, 'review_state')
                    if state != 'position_free':
                        if state == 'position_occupied' and location.getSampletemp():
                            location.setSampletemp(None)
                        wftool.doActionFor(location, action='free', wf_id='bika_storageposition_workflow')

            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()

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

    def get_storage_units(self):
        display_list = list(self.context.getStorageUnits().items())
        return display_list

    def get_freezers(self):
        display_list = list(self.context.getFreezers().items())
        return display_list

    def get_shelves(self):
        display_list = list(self.context.getShelves().items())
        return display_list

    def get_boxes(self):
        display_list = list(self.context.getBoxes().items())
        return display_list

    def get_positions(self):
        display_list = list(self.context.getPositions().items())
        return display_list

class AjaxGetFreezers:
    """
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        catalog = getToolByName(self.context, 'uid_catalog')
        brains = catalog.searchResults(portal_type='StorageUnit', UID=form['uid'])
        storage_unit = brains[0].getObject() if brains else None
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        #TODO: WE SHOULD USE IN THIS QUERY, getStorageUnit, AS A PARAMETER OF RESEARCH, BUT UNFORTUNATLY
        #TODO: I DON'T KNOW WHY IT'S NOT WORKING??? KEEP SEARCHING ON THIS OR ASK QUESTION.
        #brains = catalog.searchResults(portal_type='StorageManagement', getStorageUnit=storage_unit, sort_on='created')
        brains = catalog.searchResults(portal_type='StorageManagement',
                                       inactive_state='active',
                                       sort_on='created')
        storages = []
        for brain in brains:
            if brain.getStorageUnit == storage_unit:
                storages.append(brain)
        ret = []
        for brain in storages:
            ret.append({'uid': brain.UID, 'title': brain.title})

        return json.dumps(ret)


class AjaxGetShelves:
    """
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        catalog = getToolByName(self.context, 'uid_catalog')
        brains = catalog.searchResults(portal_type='StorageManagement', UID=form['uid'])
        storage_unit = brains[0].getObject() if brains else None
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        # TODO: WE SHOULD USE IN THIS QUERY, getStorageUnit, AS A PARAMETER OF RESEARCH, BUT UNFORTUNATELY
        # TODO: I DON'T KNOW WHY IT'S NOT WORKING??? KEEP SEARCHING ON THIS OR ASK QUESTION.
        # brains = catalog.searchResults(portal_type='StorageManagement', getStorageUnit=storage_unit, sort_on='created')
        brains = catalog.searchResults(portal_type='StorageManagement',
                                       inactive_state='active',
                                       sort_on='created')
        storages = []
        for brain in brains:
            if brain.getStorageUnit == storage_unit:
                storages.append(brain)

        ret = []
        for brain in storages:
            ret.append({'uid': brain.UID, 'title': brain.title})

        return json.dumps(ret)

class AjaxGetBoxes:
    """
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        catalog = getToolByName(self.context, 'uid_catalog')
        brains = catalog.searchResults(portal_type='StorageManagement', UID=form['uid'])
        storage_unit = brains[0].getObject() if brains else None
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        # TODO: WE SHOULD USE IN THIS QUERY, getStorageUnit, AS A PARAMETER OF RESEARCH, BUT UNFORTUNATLY
        # TODO: I DON'T KNOW WHY IT'S NOT WORKING??? KEEP SEARCHING ON THIS OR ASK QUESTION.
        # brains = catalog.searchResults(portal_type='StorageManagement', getStorageUnit=storage_unit, sort_on='created')
        brains = catalog.searchResults(portal_type='StorageManagement',
                                       inactive_state='active',
                                       sort_on='created')
        storages = []
        for brain in brains:
            if brain.getStorageUnit == storage_unit:
                storages.append(brain)

        ret = []
        for brain in storages:
            ret.append({'uid': brain.UID, 'title': brain.title})

        return json.dumps(ret)


class AjaxGetPositions:
    """
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        catalog = getToolByName(self.context, 'uid_catalog')
        brains = catalog.searchResults(portal_type='StorageManagement', UID=form['uid'])
        storage_unit = brains[0].getObject() if brains else None
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        brains = catalog.searchResults(portal_type='StorageLocation',
                                       inactive_state='active',
                                       review_state='position_free',
                                       sort_on='created')
        storages = []
        for brain in brains:
            if brain.getParentBox == storage_unit:
                storages.append(brain)

        ret = []
        for brain in storages:
            ret.append({'uid': brain.UID, 'title': brain.title})

        return json.dumps(ret)


class AjaxGetBiospecimenVolume:
    """
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        ret = {}
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        brains = catalog.searchResults(portal_type="Biospecimen", UID=form['uid'])
        biospecimen = brains[0].getObject() if brains else None
        volume = biospecimen.getVolume() if biospecimen else 0
        ret['volume'] = float(volume)

        # catalog = getToolByName(self.context, 'bika_catalog')
        # #TODO: WE ARE USING AN INDEX WE CREATED, getBiospecimen. AS WE EXPERIENCED, SOMETIMES THIS NOT
        # #TODO: WORKING. THEN BECARFUL.
        # brains = catalog.searchResults(portal_type='Sampletemp', getBiospecimen=biospecimen)
        # total_volume = 0
        # for brain in brains:
        #     obj = brain.getObject()
        #     quantity = int(obj.getQuantity()) if obj.getQuantity() else 0
        #     volume = float(obj.getVolume()) if obj.getVolume() else 0
        #     total_volume += float(quantity * volume)
        total_volume = biospecimen.getVolumeUsed()
        ret['total_volume'] = total_volume
        print ret
        return json.dumps(ret)