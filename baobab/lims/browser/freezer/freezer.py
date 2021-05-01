# -*- coding: utf-8 -*-

import json
from Products.CMFCore.utils import getToolByName
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

        self.location = self.context.getStorageUnit()
        self.location = self.location and "<a href='%s'>%s</a>" % (
                self.location.absolute_url(), self.location.Title()) or None
        self.device = self.context.getMonitoringDevice()
        self.device = self.device and "<a href='%s'>%s</a>" % (
                self.device.absolute_url(), self.device.Title()) or None
        self.temperature = self.context.getLatestTemperature()

        return self.template()


class FreezerTemperatures():
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        bc = getToolByName(context, 'bika_catalog')
        brains = bc(portal_type='DeviceReading',
                  path={'query': "/".join(context.getPhysicalPath())})
        readings = []

        # TODO: add columns
        for reading in brains:
            obj = reading.getObject()
            temperature = obj.getCurrentReading()
            datetimestamp = obj.getDatetimeRecorded()
            if datetimestamp is None or temperature is None:
                continue

            # convert datetime to plot points on highcharts, highcharts uses
            # milliseconds
            milliseconds = datetimestamp.timeTime() * 1000
            readings.append([milliseconds, float(temperature)])

        sort_readings = sorted(readings, key=lambda x: x[0])
        return json.dumps(sort_readings)
