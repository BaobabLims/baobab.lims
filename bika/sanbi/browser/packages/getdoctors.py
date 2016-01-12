from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.health.permissions import *
from bika.lims import bikaMessageFactory as _b
from bika.lims.browser import BrowserView
from operator import itemgetter
import json
import plone


class ajaxGetDoctors(BrowserView):
    """ vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request['searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']

        rows = []

        pc = self.portal_catalog
        proxies = pc(portal_type="Doctor")
        for doctor in proxies:
            doctor = doctor.getObject()
            if self.portal_workflow.getInfoFor(doctor, 'inactive_state', 'active') == 'inactive':
                continue
            if doctor.Title().lower().find(searchTerm) > -1 \
            or doctor.getDoctorID().lower().find(searchTerm) > -1:
                rows.append({'Title': doctor.Title() or '',
                             'DoctorID': doctor.getDoctorID(),
                             'DoctorSysID': doctor.id,
                             'DoctorUID': doctor.UID()})

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()), key = itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'pages': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
