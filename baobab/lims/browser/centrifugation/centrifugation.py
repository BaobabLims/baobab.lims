# import os
# import traceback

from DateTime import DateTime
from Products.ATContentTypes.lib import constraintypes
# from Products.Archetypes.public import BaseFolder
from Products.CMFCore.utils import getToolByName
# from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone.app.content.browser.interfaces import IFolderContentsView
# from plone.app.layout.globals.interfaces import IViewView
# from zope.interface import implements

#from Products.Five.browser import BrowserView
from bika.lims.browser import BrowserView
# from bika.lims.browser.bika_listing import BikaListingView
# from bika.lims.browser.multifile import MultifileView
# from bika.lims.utils import to_utf8
# from baobab.lims import bikaMessageFactory as _
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime

import json


class CentrifugationView(BrowserView):
    template = ViewPageTemplateFile('templates/centrifugation_view.pt')

    def __init__(self, context, request):
        super(CentrifugationView, self).__init__(context, request)
        self.title = self.context.Title()
        self.context = context
        self.request = request

    def __call__(self):

        workflow = getToolByName(self.context, 'portal_workflow')
        reviewState = workflow.getInfoFor(self.context, 'review_state')

        self.reviewState = reviewState
        self.absolute_url = self.context.absolute_url()
        self.id = self.context.getId()
        self.sample_pooling_uid = self.context.UID()

        self.title = self.context.Title()
        self.description = self.context.Description()
        self.date_created = self.context.getDateCreated()
        self.selected_sample = self.context.get_selected_sample()
        self.technician = self.context.get_technician()
        self.technique= self.context.getTechnique()

        self.centrifugation_rows = self.prepare_centrifugation_rows()

        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

    def prepare_centrifugation_rows(self):

        centrifugation_rows = self.context.get_centrifugation_rows()
        prepared_samples = []

        for sample in centrifugation_rows:
            prepared_sample = {
                'title': sample.Title(),
                'location': self.get_storage_location(sample),
                'condition': self.get_sample_condition(sample),
                'volume': sample.getField('Volume').get(sample),
                'unit': sample.getField('Unit').get(sample),
            }
            prepared_samples.append(prepared_sample)

        return prepared_samples

    def get_storage_location(self, sample):
        try:
            storage_location = sample.getStorageLocation()
            return storage_location.Title()
        except:
            return ''

    def get_sample_condition(self, sample):
        try:
            sample_condition = sample.getField('SampleCondition').get(sample)
            return sample_condition.Title()
        except:
            return ''

class CentrifugationEdit(BrowserView):
    # template = ViewPageTemplateFile('templates/sample_shipment_edit.pt')
    template = ViewPageTemplateFile('templates/centrifugation_edit.pt')

    def __call__(self):
        request = self.request
        context = self.context

        if 'submitted' in request:
            print('----------centrifugation')
            print(self.request.form)

            context.setConstrainTypesMode(constraintypes.DISABLED)

            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)

            self.perform_centrifugation_audit(self.context, request)
            context.getField('description').set(context, self.request.form['description'])
            context.getField('DateCreated').set(context, self.request.form['DateCreated'])
            context.getField('SelectedSample').set(context, self.request.form['SelectedSample_uid'])
            context.getField('Technician').set(context, self.request.form['Technician_uid'])
            context.getField('Technique').set(context, self.request.form['Technique'])
            context.reindexObject()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return

        return self.template()

    def perform_centrifugation_audit(self, centrifugation, request):
        audit_logger = AuditLogger(self.context, 'Centrifugation')
        pc = getToolByName(self.context, "portal_catalog")

        # Description
        if centrifugation.getField('description').get(centrifugation) != request.form['description']:
            audit_logger.perform_simple_audit(centrifugation, 'description', centrifugation.getField('description').get(centrifugation),
                                              request.form['description'])

        # Date Created
        date_created = request.form['DateCreated']
        # if date_created:
        #     date_created = DateTime(getLocalServerTime(date_created))
        object_date_created = centrifugation.getField('DateCreated').get(centrifugation)
        if not object_date_created:
            object_date_created = ''
        if object_date_created != date_created:
            audit_logger.perform_simple_audit(centrifugation, 'DateCreated',
                                              object_date_created, date_created)

        # Selected Sample
        audit_logger.perform_reference_audit(centrifugation, 'SelectedSample', centrifugation.getField('SelectedSample').get(centrifugation),
                                             pc, request.form['SelectedSample_uid'])

        # Technician
        audit_logger.perform_reference_audit(centrifugation, 'Technician',
                                             centrifugation.getField('Technician').get(centrifugation),
                                             pc, request.form['Technician_uid'])

        # Technique
        if centrifugation.getField('Technique').get(centrifugation) != request.form['Technique']:
            audit_logger.perform_simple_audit(centrifugation, 'Technique',
                                              centrifugation.getField('Technique').get(centrifugation),
                                              request.form['Technique'])

    def get_fields_with_visibility(self, visibility, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            accepted_fields = ['title', 'description', 'DateCreated', 'SelectedSample', 'Technician', 'Technique']
            if v == visibility and field.getName() in accepted_fields:
                fields.append(field)
        return fields

class GetCentrifugationData(BrowserView):

    def __init__(self, context, request):

        super(GetCentrifugationData, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        uc = getToolByName(self.context, 'portal_catalog')

        try:
            uid = self.request['UID']
            brains = uc.searchResults(portal_type='Centrifugation', UID=uid)
            sample_pooling = brains[0].getObject()

            return_val = {
                'date_created': str(sample_pooling.getField('DateCreated').get(sample_pooling) or ''),
            }

            return json.dumps(return_val)

        except:
            return json.dumps({
                'date_created': '',
            })


class ajaxGetProjects(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetProjects, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        # plone.protect.CheckAuthenticator(self.request)
        rows = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="Project")

        for project in brains:
            rows.append({
                project.UID: project.Title
            })

        return json.dumps(rows)


class ajaxGetSampleTypes(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetSampleTypes, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        # plone.protect.CheckAuthenticator(self.request)
        rows = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="SampleType")

        for sample_type in brains:
            rows.append({
                sample_type.UID: sample_type.Title
            })

        return json.dumps(rows)
