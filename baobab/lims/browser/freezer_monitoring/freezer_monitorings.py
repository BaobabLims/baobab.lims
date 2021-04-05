import requests
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


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
        api_token = ''
        email = ''
        password = ''
        login = "https://apiwww.easylogcloud.com/Users.svc/Login"
        payload = {'APIToken': api_token, 'email': email,
                   'password': password}
        logged_in = requests.get(login, params=payload)
        if logged_in.status_code == 200:
            data = logged_in.json()
        else:
            return logged_in

        userguid = data['GUID']
        mac_address = '98:8B:AD:28:04:26'
        current_readings = "https://apiwww.easylogcloud.com/Devices.svc/CurrentReadings"
        payload = {'APIToken': api_token, 'userGUID': userguid,
                   'MAC_ADDRESS': mac_address, 'localTime': 'true'}
        received_readings = requests.get(current_readings, params=payload)
        data = received_readings.json()
        readings = data.get('channels', [])

        # Freezer the device is currently on
        pc = getToolByName(self.context, 'portal_catalog')
        freezer = pc(portal_type="Freezer", device_uid=device_uid)
        mon_device = pc(portal_type="MonitoringDevice", uid=device_uid)

        # Device Reading
        for reading in readings:
            freezer_reading = _createObjectByType('DeviceReading', freezer, tmpID())
            freezer_reading.setCurrentReading(reading[''])
            freezer_reading.setLabel(reading[''])
            freezer_reading.setDecimalPlaces(reading[''])
            freezer_reading.setUnit(reading[''])
            freezer_reading.unmarkCreationFlag()
            renameAfterCreation(freezer_reading)

            device_reading = _createObjectByType('DeviceReading', mon_device, tmpID())
            device_reading.setCurrentReading(reading[''])
            device_reading.setLabel(reading[''])
            device_reading.setDecimalPlaces(reading[''])
            device_reading.setUnit(reading[''])
            device_reading.unmarkCreationFlag()
            renameAfterCreation(device_reading)

        return 'Done'
