from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class CheckNewExpiredItems(ViewletBase):

    index = ViewPageTemplateFile("templates/expired_items_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        ViewletBase.__init__(self, context, request, view, manager=manager)
        self.nr_expired = 0
        self.expired_items = []

    def get_expired_items (self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        workflow = getToolByName(self.context, 'portal_workflow')
        # Check for new expired items
        brains = bsc(portal_type='StockItem', review_state='available')
        for brain in brains:
            obj = brain.getObject()
            expiry_date = obj.getExpiryDate()
            if expiry_date and not expiry_date.isFuture():
                workflow.doActionFor(obj, 'expire')

        brains = bsc(portal_type="StockItem", review_state='expired')
        for brain in brains:
            obj = brain.getObject()
            expiry_date = obj.getExpiryDate()
            if expiry_date and expiry_date.isFuture():
                workflow.doActionFor(obj, 'reinstate')
                continue
            item = {
                'uid': obj.UID(),
                'title': obj.Title(),
            }
            self.nr_expired += 1
            item['link'] = '<a href="%s">%s</a>' % (
                obj.absolute_url(), obj.Title()
            )
            self.expired_items.append(item)

    def render(self):

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        allowed = 'LabManager' in roles or 'Manager' in roles

        self.get_expired_items()

        if allowed and self.nr_expired:
            return self.index()
        else:
            return ""
