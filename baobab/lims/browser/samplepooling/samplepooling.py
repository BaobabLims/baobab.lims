# import os
# import traceback

from DateTime import DateTime
from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime

import json
from baobab.lims.utils.permissions_check import is_administrator



class SamplePoolingView(BrowserView):
    template = ViewPageTemplateFile('templates/sample_pooling_view.pt')

    def __init__(self, context, request):
        super(SamplePoolingView, self).__init__(context, request)
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
        self.analyst = self.get_analyst()

        self.input_samples = self.prepare_input_samples()
        self.intermediate_samples = self.prepare_intermediate_samples()
        self.result_samples = self.prepare_result_samples()

        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

    def prepare_input_samples(self):

        input_samples = self.context.getInputSamples()

        prepared_samples = []
        for input_sample in input_samples:
            sample = input_sample.getField('SelectedSample').get(input_sample)
            if not sample:
                continue
            prepared_sample = {
                'title': sample.Title(),
                'location': self.get_storage_location(sample),
                'volume': input_sample.getField('InputVolume').get(input_sample),
                'unit': sample.getField('Unit').get(sample),
            }
            prepared_samples.append(prepared_sample)

        return prepared_samples

    def prepare_intermediate_samples(self):

        intermediate_sample = self.context.get_intermediate_sample()

        if not intermediate_sample:
            return []

        # intermediate_samples = self.context.getIntermediateSamples()
        storage_location = self.get_storage_location(intermediate_sample)
        # print(intermediate_sample.getField('StorageLocation').get(intermediate_sample))
        # print(intermediate_sample.__dict__)

        samples = [
            {
                'title': intermediate_sample.Title(),
                'location': self.get_storage_location(intermediate_sample),
                'volume': intermediate_sample.getField('Volume').get(intermediate_sample),
                'unit': intermediate_sample.getField('Unit').get(intermediate_sample),
            }
        ]

        return samples

    def get_analyst(self):
        try:
            analyst = self.context.getAnalyst()
            return analyst.Title()
        except:
            return ''


    def prepare_result_samples(self):

        result_samples = self.context.getResultSamples()

        prepared_samples = []
        for result_sample in result_samples:
            sample = result_sample.getField('FinalSample').get(result_sample)
            if not sample:
                continue
            prepared_sample = {
                'title': sample.Title(),
                'location': self.get_storage_location(sample),
                'volume': result_sample.getField('FinalVolume').get(result_sample),
                'unit': result_sample.getField('FinalVolumeUnit').get(result_sample),
            }
            prepared_samples.append(prepared_sample)
        #
        # print('------------Result samples')
        # print(prepared_samples)

        return prepared_samples

    def get_storage_location(self, sample):

        return sample.getStorageLocation() and sample.getStorageLocation().Title() or ''


class SamplePoolingEdit(BrowserView):
    # template = ViewPageTemplateFile('templates/sample_shipment_edit.pt')
    template = ViewPageTemplateFile('templates/sample_pooling_edit.pt')

    def __call__(self):
        # portal = self.portal
        request = self.request
        context = self.context
        # setup = portal.bika_setup

        if 'submitted' in request:
            context.setConstrainTypesMode(constraintypes.DISABLED)

            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)

            # self.perform_sample_shipment_audit(self.context, request)
            context.getField('description').set(context, self.request.form['description'])
            context.getField('DateCreated').set(context, self.request.form['DateCreated'])
            context.getField('Analyst').set(context, self.request.form['Analyst_uid'])
            context.reindexObject()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return

        # self.is_admin_user = True
        self.is_admin_user = is_administrator(self.context)
        return self.template()

    def perform_sample_shipment_audit(self, sample_shipment, request):
        audit_logger = AuditLogger(self.context, 'SampleShipment')
        pc = getToolByName(self.context, "portal_catalog")

        audit_logger.perform_multi_reference_audit(sample_shipment, 'SamplesList',
                                                                sample_shipment.getField('SamplesList').get(sample_shipment),
                                                                pc, request.form['SamplesList_uid'])

        if sample_shipment.getField('FromEmailAddress').get(sample_shipment) != request.form['FromEmailAddress']:
            audit_logger.perform_simple_audit(sample_shipment, 'FromEmailAddress', sample_shipment.getField('FromEmailAddress').get(sample_shipment),
                                              request.form['FromEmailAddress'])

        if sample_shipment.getField('ToEmailAddress').get(sample_shipment) != request.form['ToEmailAddress']:
            audit_logger.perform_simple_audit(sample_shipment, 'ToEmailAddress', sample_shipment.getField('ToEmailAddress').get(sample_shipment),
                                              request.form['ToEmailAddress'])

        audit_logger.perform_reference_audit(sample_shipment, 'Client', sample_shipment.getField('Client').get(sample_shipment),
                                             pc, request.form['Client_uid'])

        if sample_shipment.getField('DeliveryAddress').get(sample_shipment) != request.form['DeliveryAddress']:
            audit_logger.perform_simple_audit(sample_shipment, 'DeliveryAddress', sample_shipment.getField('DeliveryAddress').get(sample_shipment),
                                              request.form['DeliveryAddress'])

        if sample_shipment.getField('BillingAddress').get(sample_shipment) != request.form['BillingAddress']:
            audit_logger.perform_simple_audit(sample_shipment, 'BillingAddress', sample_shipment.getField('BillingAddress').get(sample_shipment),
                                              request.form['BillingAddress'])

        # shipping date audit
        form_shipping_date = request.form['ShippingDate']
        if form_shipping_date:
            form_shipping_date = DateTime(getLocalServerTime(form_shipping_date))
        object_shipping_date = sample_shipment.getField('ShippingDate').get(sample_shipment)
        if not object_shipping_date:
            object_shipping_date = ''
        if object_shipping_date != form_shipping_date:
            audit_logger.perform_simple_audit(sample_shipment, 'ShippingDate', object_shipping_date, form_shipping_date)

        # date dispatched audit
        date_dispatched = request.form['DateDispatched']
        if date_dispatched:
            date_dispatched = DateTime(getLocalServerTime(date_dispatched))
        object_date_dispatched = sample_shipment.getField('DateDispatched').get(sample_shipment)
        if not object_date_dispatched:
            object_date_dispatched = ''
        if object_date_dispatched != date_dispatched:
            audit_logger.perform_simple_audit(sample_shipment, 'DateDispatched',
                                              object_date_dispatched, date_dispatched)

        # date delivered audit
        date_delivered = request.form['DateDelivered']
        if date_delivered:
            date_delivered = DateTime(getLocalServerTime(date_delivered))
        object_date_delivered = sample_shipment.getField('DateDelivered').get(sample_shipment)
        if not object_date_delivered:
            object_date_delivered = ''
        if object_date_delivered != date_delivered:
            audit_logger.perform_simple_audit(sample_shipment, 'DateDelivered',
                                              object_date_delivered, date_delivered)

        if sample_shipment.getField('Courier').get(sample_shipment) != request.form['Courier']:
            audit_logger.perform_simple_audit(sample_shipment, 'Courier', sample_shipment.getField('Courier').get(sample_shipment),
                                              request.form['Courier'])

        if sample_shipment.getField('CourierInstructions').get(sample_shipment) != request.form['CourierInstructions']:
            audit_logger.perform_simple_audit(sample_shipment, 'CourierInstructions', sample_shipment.getField('CourierInstructions').get(sample_shipment),
                                              request.form['CourierInstructions'])

        if sample_shipment.getField('TrackingURL').get(sample_shipment) != request.form['TrackingURL']:
            audit_logger.perform_simple_audit(sample_shipment, 'TrackingURL', sample_shipment.getField('TrackingURL').get(sample_shipment),
                                              request.form['TrackingURL'])

        # Shipment condition audit
        if sample_shipment.getField('ShipmentConditions').get(sample_shipment) != request.form['ShipmentConditions']:
            audit_logger.perform_simple_audit(sample_shipment, 'ShipmentConditions', sample_shipment.getField('ShipmentConditions').get(sample_shipment),
                                              request.form['ShipmentConditions'])

        # Shipping costs audit
        form_shipping_cost = request.form['ShippingCost']
        if not form_shipping_cost:
            form_shipping_cost = 0
        else:
            form_shipping_cost = float(form_shipping_cost)

        object_shipping_cost = sample_shipment.getField('ShippingCost').get(sample_shipment)
        if not object_shipping_cost:
            object_shipping_cost = 0
        else:
            object_shipping_cost = float(object_shipping_cost)

        if form_shipping_cost != object_shipping_cost:
            audit_logger.perform_simple_audit(sample_shipment, 'ShippingCost', object_shipping_cost,
                                              form_shipping_cost)

        # The weight audit
        form_weight = request.form['Weight']
        if not form_weight:
            form_weight = 0
        else:
            form_weight = float(form_weight)

        object_weight = sample_shipment.getField('Weight').get(sample_shipment)
        if not object_weight:
            object_weight = 0
        else:
            object_weight = float(object_weight)

        if object_weight != form_weight:
            audit_logger.perform_simple_audit(sample_shipment, 'Weight', object_weight, form_weight)

        if sample_shipment.getField('Volume').get(sample_shipment) != request.form['Volume']:
            audit_logger.perform_simple_audit(sample_shipment, 'Volume', sample_shipment.getField('Volume').get(sample_shipment),
                                              request.form['Volume'])

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

    def get_sample_pooling_uid(self):
        uid = self.context.UID()
        print('-----This is UID')
        print(uid)
        return uid



    # def get_fields_with_visibility(self, visibility, schemata, mode=None):
    #     mode = mode if mode else 'edit'
    #     schema = self.context.Schema()
    #     fields = []
    #     for field in schema.fields():
    #
    #         isVisible = field.widget.isVisible
    #         v = isVisible(self.context, mode, default='invisible', field=field)
    #         if v == visibility:
    #
    #             if field.schemata == schemata:
    #                 fields.append(field)
    #
    #     return fields

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
