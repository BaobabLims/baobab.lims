from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser.dashboard import DashboardView as DV


class DashboardView(DV):
    template = ViewPageTemplateFile("templates/dashboard.pt")
