from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from baobab.lims import bikaMessageFactory as _


class MultimagesView(BikaListingView):
    """
    This class implements a bika listing base view. This view is thought to be
    used inside other content types actions as a default way to upload and
    show images for biospecimens.
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(MultimagesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'Multimage',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=Multimage',
                                     'icon':
                                         '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "multimage"
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images" \
                    "/instrumentcertification_big.png"
        self.title = self.context.translate(_("Images"))
        self.description = ""

        self.columns = {
            "DocumentID": {'title': _("Document ID"),
                           'index': 'sortable_title'},
            "SmallDesc": {'title': _("Description"),
                          'index': 'sortable_title'},
            "DatetimeCreated": {'title': _("Date Creation"),
                                'toggle': False},
            'FileDownload': {'title': _('File')}
        }

        self.review_states = [
            {'id': 'default',
             'title': _("All"),
             'contentFilter': {},
             'columns': ['DocumentID',
                         'SmallDesc',
                         'FileDownload',
                         'DatetimeCreated']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for val in self.context.getDocuments():
            toshow.append(val.UID())

        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            if obj.UID() in toshow:
                items[x]['replace']['DocumentID'] = "<a href='%s'>%s</a>" % \
                                                    (items[x]['url'],
                                                     items[x]['DocumentID'])
                items[x]['SmallDesc'] = obj.getSmallDescription()
                items[x]['FileDownload'] = obj.getFile().filename
                filename = obj.getFile().filename if obj.getFile().filename \
                                                     != '' else 'Image'
                items[x]['replace']['FileDownload'] = "<a href='%s'>%s</a>" % \
                                                      (
                                                      obj.getFile().absolute_url_path(),
                                                      filename)
                items[x]['DatetimeCreated'] = self.ulocalized_time(
                    obj.getDatetimeCreated())
                outitems.append(items[x])
        return outitems


class MultimageView(BrowserView):
    template = ViewPageTemplateFile("templates/multimage_view.pt")
    title = _("Managing Storage")

    def __call__(self):
        context = self.context
        request = self.request
        portal = self.portal

        self.filename = context.getFile().filename
        self.path = context.getFile().absolute_url_path()
        self.size = context.get_size()
        self.full_screen = self.path + "/image_view_fullscreen"
        self.image_src = self.path + "/image_preview"
        self.download = self.path + "/download"
        self.search_icon = portal.absolute_url() + "/search_icon.png"
        self.download_icon = portal.absolute_url() + "/download_icon.png"

        return self.template()
