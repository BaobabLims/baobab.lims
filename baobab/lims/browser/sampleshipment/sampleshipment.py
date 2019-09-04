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


class SampleShipmentView(BrowserView):
    template = ViewPageTemplateFile('templates/sample_shipment_view.pt')

    def __init__(self, context, request):
        super(SampleShipmentView, self).__init__(context, request)
        self.title = self.context.Title()
        self.context = context
        self.request = request

    def __call__(self):

        samples = self.context.getSamplesList()

        workflow = getToolByName(self.context, 'portal_workflow')
        reviewState = workflow.getInfoFor(self.context, 'review_state')

        self.reviewState = reviewState
        self.absolute_url = self.context.absolute_url()
        self.id = self.context.getId()
        self.sample_shipment_uid = self.context.UID()
        self.title = self.context.Title()
        self.description = self.context.Description()
        self.from_contact = self.context.getFromEmailAddress()
        self.to_contact = self.context.getToEmailAddress()
        self.client = self.context.getClient().Title()
        self.delivery_address = self.context.getDeliveryAddress()
        self.shipping_date = self.context.getShippingDate()
        self.date_dispatched = self.context.getDateDispatched()
        self.date_delivered = self.context.getDateDelivered()
        self.courier_name = self.context.getCourier()
        self.courier_instructions = self.context.getCourierInstructions()
        self.tracking_url = self.context.getTrackingURL()
        self.shipment_conditions = self.context.getShipmentConditions()
        self.shipping_cost = self.context.getShippingCost()
        self.weight = self.context.getWeight()
        self.volume = self.context.getVolume()
        self.samples = samples     # self.context.getSamplesList()
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

class SampleShipmentEdit(BrowserView):
    # template = ViewPageTemplateFile('templates/sample_shipment_edit.pt')
    template = ViewPageTemplateFile('templates/sample_shipment_edit.pt')

    def __call__(self):
        # print('----SampleShipment call---------')
        # portal = self.portal
        request = self.request
        context = self.context
        # setup = portal.bika_setup

        if 'submitted' in request:
            context.setConstrainTypesMode(constraintypes.DISABLED)

            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)

            self.perform_sample_shipment_audit(self.context, request)

            context.processForm()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return

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



    def get_fields_with_visibility(self, visibility, schemata, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():

            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:

                if field.schemata == schemata:
                    fields.append(field)

        return fields
