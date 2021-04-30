# -*- coding: utf-8 -*-

import re
import requests
from datetime import datetime as dt
from DateTime import DateTime as DT
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone import api as ploneapi

from bika.lims.browser import BrowserView
from bika.lims.utils import tmpID

from baobab.lims.idserver import renameAfterCreation


class FreezerMonitoringView(BrowserView):
    template = ViewPageTemplateFile("templates/freezer_monitorings.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        return self.template()


class FreezerMonitoringCron(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        # Login
        bc = getToolByName(ploneapi.portal.get(), 'bika_catalog')
        form = self.request.form

        api_token = form.get('API_TOKEN')
        email = form.get('email')
        password = form.get('password')
        url = "https://apiwww.easylogcloud.com/"
        login = url + "Users.svc/Login"
        payload = {'APIToken': api_token, 'email': email,
                   'password': password}
        logged_in = requests.get(login, params=payload)
        if logged_in.status_code == 200:
            data = logged_in.json()
        else:
            return logged_in

        user_guid = data['GUID']

        # AllDevicesSummary to get the sensorUID
        devices_url = url + 'Devices.svc/AllDevicesSummary'
        payload = {'APIToken': api_token,
                   'userGUID': user_guid,
                   'includeArchived': 'false'}
        devices = requests.get(devices_url, params=payload)
        if devices.status_code == 200:
            devices_data = devices.json()
        else:
            return devices

        for device in devices_data:
            sensor_guid = device['GUID']
            # Current readings
            current_readings = url + "Devices.svc/CurrentReadings"
            payload = {'APIToken': api_token,
                       'userGUID': user_guid,
                       'sensorGUID': sensor_guid,
                       'localTime': 'true'}
            received_readings = requests.get(current_readings, params=payload)
            if received_readings.status_code == 200:
                received_readings_data = received_readings.json()
            else:
                # TODO: Log error
                continue

            mon_device = bc(portal_type="MonitoringDevice",
                            getMACAddress=device['MACAddress'])
            if not mon_device:
                # TODO: Log error
                continue

            # Freezer the device is currently on
            device_uid = mon_device[0].UID
            mon_device_obj = mon_device[0].getObject()
            freezer = bc(portal_type="Freezer",
                        getMonitoringDeviceUID=device_uid)
            if not freezer:
                # TODO: Log error
                continue

            freezer_obj = freezer[0].getObject()
            self.create_freezer_readings(received_readings_data, freezer_obj)

    def create_freezer_readings(self, readings, freezer):
        # Device Reading
        # slice out \xb0C on the result because it throws an ascii error
        # unit defaults to °C so we can avoid the ascii error
        current_reading = readings['channels'][0]
        # Date comes back as u'/Date(1619779624000+0000)/'
        record_date = readings['datetime']
        record_date = dt.fromtimestamp(int(
            re.findall(r"\d+", record_date)[0]) / 1000)

        freezer_reading = _createObjectByType('DeviceReading',
                                              freezer,
                                              tmpID())
        freezer_reading.setCurrentReading(float(current_reading[0:-2]))
        freezer_reading.setDatetimeRecorded(DT(record_date))
        unit = freezer_reading.getUnit() + str(current_reading[-1])
        freezer_reading.setUnit(unit)
        freezer_reading.unmarkCreationFlag()
        renameAfterCreation(freezer_reading)

        return 'Done'
