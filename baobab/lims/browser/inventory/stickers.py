from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Sticker(BrowserView):
    """Labels of stock items of an order"""

    def __call__(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        items = self.request.get('items', '')
        if items:
            self.items = [o.getObject() for o in bsc(id=items.split(","))]
        else:
            self.items = [self.context,]

        # Orders get stickers for their stock items
        new_items = []
        for i in self.items:
            if i.portal_type == 'InventoryOrder':
                catalog = bsc(portal_type='StockItem')
                new_items += [pi.getObject() for pi in catalog
                              if pi.getObject().getOrderId() == i.getId()]
            else:
                new_items.append(i)
        self.items = new_items

        if not self.items:
            logger.warning("Cannot print stickers: no items specified in request")
            self.request.response.redirect(self.context.absolute_url())
            return

        template = 'templates/stickers/sticker_stockitem_small.pt'
        stickertemplate = ViewPageTemplateFile(template)
        return stickertemplate(self)
