from Products.CMFPlone.utils import _createObjectByType
from zope import event

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter, methodcaller

from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView

from bika.lims.utils import t
import json
import plone

class View(BrowserView):

    template = ViewPageTemplateFile('templates/supplyex_view.pt')
    title = _('Supply Ex')

    def __call__(self):
        context = self.context
        portal = self.portal
        setup = portal.bika_setup
        # Disable the add new menu item
        context.setConstrainTypesMode(1)
        context.setLocallyAllowedTypes(())

        # Render the template
        return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/supplyex_edit.pt')
    field = ViewPageTemplateFile('templates/row_field.pt')

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup

        if 'submit' in request:
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return
        else:
            # Render the template
            return self.template()

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

class PrintView(View):

    template = ViewPageTemplateFile('templates/supplyex_print.pt')

    def __call__(self):
        return View.__call__(self)
