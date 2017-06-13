import os
import traceback

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims import logger
from bika.lims.browser import BrowserView
from baobab.lims import bikaMessageFactory as _


class Sticker(BrowserView):
    """Labels of assembled kits"""
    _TEMPLATES_DIR = 'templates/stickers'

    def __call__(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        items = self.request.get('items', '')
        if items:
            self.items = [o.getObject() for o in bsc(id=items.split(","))]
        else:
            self.items = [self.context, ]

        new_items = []
        for i in self.items:
            if i.portal_type == "Kit":
                catalog = bsc(portal_type="StockItem")
                brains = bsc.searchResults({'portal_type': 'Product',
                                            'title': i.getKitTemplate().Title()})

                if len(brains) == 1:
                    new_items += [pi.getObject() for pi in catalog
                                  if
                                  pi.getObject().getProduct().getId() == brains[
                                      0].getObject().getId()]
        self.items = new_items
        if not self.items:
            logger.warning(
                "Cannot print sticker: no items specified in request")
            self.request.response.redirect(self.context.absolute_url())
            return

        template = 'templates/stickers/sticker_kits_small.pt'
        stickertemplate = ViewPageTemplateFile(template)
        return stickertemplate(self)

    def getCSS(self):
        template_name = 'sticker_kit.pt'
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
        path = '%s/%s.css' % (templates_dir, template_name[:-3])
        with open(path, 'r') as content_file:
            content = content_file.read()

        return content

    def renderSTemplate(self):
        templates_dir = self._TEMPLATES_DIR
        template_name = 'sticker_kit.pt'

        embed = ViewPageTemplateFile(os.path.join(templates_dir, template_name))
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except:
            tbex = traceback.format_exc()
            ktid = self.context.id
            reptemplate = "<div class='error-print'>%s - %s '%s':<pre>%s</pre></div>" % (
                ktid, _("Unable to load the template"), template_name, tbex)

        return reptemplate
