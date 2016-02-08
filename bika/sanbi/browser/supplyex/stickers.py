from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Sticker(BrowserView):
    """Labels of assembled kits"""

    def __call__(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        items = self.request.get('items', '')
        if items:
            self.items = [o.getObject() for o in bsc(id=items.split(","))]
        else:
            self.items = [self.context,]

        new_items = []
        for i in self.items:
            if i.portal_type == "SupplyEx":
                catalog = bsc(portal_type="StockItem")
                brains = bsc.searchResults({'portal_type': 'Product', 'title': i.getKitTemplate().Title()})

                if len(brains) == 1:
                    new_items += [pi.getObject() for pi in catalog
                                 if pi.getObject().getProduct().getId() == brains[0].getObject().getId()]
        self.items = new_items

        if not self.items:
            logger.warning("Cannot print sticker: no items specified in request")
            self.request.response.redirect(self.context.absolute_url())
            return

        template = 'templates/stickers/sticker_kits_small.pt'
        stickertemplate = ViewPageTemplateFile(template)
        return stickertemplate(self)