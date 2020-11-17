from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims.locales import COUNTRIES,STATES,DISTRICTS
import json
# from plone import api
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone.app.layout.viewlets import ViewletBase
# from zope.schema import ValidationError
# from DateTime import DateTime
#
# from Products.CMFPlone.utils import _createObjectByType
# from baobab.lims.idserver import renameAfterCreation
#
# from bika.lims.utils import tmpID
# from bika.lims.workflow import doActionFor

# import plone
#
# from operator import itemgetter
#
# from baobab.lims.interfaces import IUnmanagedStorage, IStoragePosition, \
#     IManagedStorage

class ajaxGetStates(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetStates, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        try:
            states = []

            country = self.request.form['country']
            if country:

                iso = [c for c in COUNTRIES if c['Country'] == country or c['ISO'] == country]

                if iso:
                    iso = iso[0]['ISO']
                    items = [x for x in STATES if x[0] == iso]
                    items.sort(lambda x, y: cmp(x[2], y[2]))
                    states = [{x[2]: x[2]} for x in items]

        except Exception as e:
            states = []

        return json.dumps(states)

class ajaxGetInstruments(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetInstruments, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        rows = []
        selected_type = self.get_content_type(self.request.form['selected_type'], 'bika_setup_catalog')

        bsc = getToolByName(self, 'bika_setup_catalog')
        brains = bsc(portal_type = 'Instrument', inactive_state = 'active')
        for brain in brains:
            try:
                instrument = brain.getObject()
                instrument_type = instrument.getInstrumentType()
                if instrument_type.Title() == selected_type.Title():
                    rows.append({instrument.UID(): instrument.Title()})
            except Exception as e:
                pass

        print('----------instruments')
        print(rows)

        return json.dumps(rows)

    def get_content_type(self, content_type_uid, catalog="portal_catalog"):
        try:
            catalog = self.get_catalog(catalog)
            brains = catalog(UID=content_type_uid)
            return brains[0].getObject()
        except Exception as e:
            return None

    def get_catalog(self, catalog="portal_catalog"):
        if catalog == 'bika_setup_catalog':
            return getToolByName(self.context, 'bika_setup_catalog')

        if catalog == 'portal_catalog':
            return getToolByName(self.context, 'portal_catalog')




        # pc = getToolByName(self.context, 'portal_catalog')
        # brains = pc(portal_type="StorageUnit")
        #
        # for storage_unit in brains:
        #     storage_unit = storage_unit.getObject()
        #
        #     rows.append({
        #         storage_unit.UID(): storage_unit.getHierarchy()
        #     })
        #
        # return json.dumps(rows)