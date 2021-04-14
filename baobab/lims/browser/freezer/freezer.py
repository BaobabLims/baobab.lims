# -*- coding: utf-8 -*-

import json
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView


class FreezerView(BrowserView):
    template = ViewPageTemplateFile('templates/freezer.pt')

    def __init__(self, context, request):
        super(FreezerView, self).__init__(context, request)
        self.title = self.context.Title()
        self.context = context
        self.request = request

    def __call__(self):

        self.location =self.context.getStorageUnit()
        self.location = self.location and "<a href='%s'>%s</a>" % (
                self.location.absolute_url(), self.location.Title()) or None
        self.device = self.context.getMonitoringDevice()
        self.device = self.device and "<a href='%s'>%s</a>" % (
                self.device.absolute_url(), self.device.Title()) or None
        self.temperature = self.context.getCurrentTemperature()

        return self.template()


class FreezerTemperatures():
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        data = api.content.find(context=context, portal_type='DeviceReading')
        readings = []

        # TODO: add columns
        for reading in data:
            obj = reading.getObject()
            temperature = obj.getCurrentReading()
            datetimestamp = obj.getDatetimeRecorded()
            if datetimestamp is None or temperature is None:
                continue
            int_date = int(datetimestamp.strftime('%s'))
            readings.append([int_date, float(temperature)])

        return json.dumps(readings)
