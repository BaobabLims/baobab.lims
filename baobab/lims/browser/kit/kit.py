import os
import traceback
from operator import itemgetter

from DateTime import DateTime
from Products.Archetypes.public import BaseFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView
from baobab.lims import bikaMessageFactory as _
from baobab.lims.browser import _lab_data, _printedby_data, _createdby_data
from baobab.lims.browser.biospecimens.biospecimens import BiospecimensView


class KitView(BrowserView):
    template = ViewPageTemplateFile('templates/kit_view.pt')
    title = _("Kit's components")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):

        context = self.context
        portal = self.portal

        self.absolute_url = context.absolute_url()
        setup = portal.bika_setup
        # Disable the add new menu item
        context.setConstrainTypesMode(1)
        context.setLocallyAllowedTypes(())
        # Collect general data
        self.st_icon = self.portal_url + \
                       "/++resource++baobab.lims.images/inventory.png"
        self.id = context.getId()
        self.title = context.Title()
        self.project = context.aq_parent.Title()
        kit_template = context.getKitTemplate()
        self.kit_template_title = kit_template and kit_template.Title() or ''
        self.items = kit_template and kit_template.kit_components() or []
        self.subtotal = kit_template and '%.2f' % kit_template.getSubtotal() or '0.00'
        self.vat = kit_template and '%.2f' % kit_template.getVATAmount() or '0.00'
        self.total = kit_template and '%.2f' % float(kit_template.getTotal()) or '0.00'

        self.items = sorted(self.items, key=itemgetter('title'))
        if 'form.action.addKitAttachment' in self.request:
            self.addKitAttachment()
        elif 'form.action.delARAttachment' in self.request:
            self.delARAttachment()

        # Render the template
        return self.template()

    def delARAttachment(self):
        """ delete the attachment """
        tool = getToolByName(self, "reference_catalog")
        if 'Attachment' in self.request.form:
            attachment_uid = self.request.form['Attachment']
            attachment = tool.lookupObject(attachment_uid)

        others = self.context.getAttachment()
        attachments = []
        for other in others:
            if not other.UID() == attachment_uid:
                attachments.append(other.UID())
        self.context.setAttachment(attachments)
        kits = attachment.aq_parent
        ids = [attachment.getId(), ]
        BaseFolder.manage_delObjects(kits, ids, self.request)

        # self.request.RESPONSE.redirect(self.context.absolute_url())
        self.request.RESPONSE.redirect(
            self.request.REQUEST.get_header('referer'))

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()

    def addKitAttachment(self, REQUEST=None, RESPONSE=None):
        workflow = getToolByName(self, 'portal_workflow')
        this_file = self.request.form['AttachmentFile_file']
        attachmentid = self.context.generateUniqueId('Attachment')
        attachment = _createObjectByType("Attachment", self.context.aq_parent,
                                         attachmentid)
        attachment.edit(
            AttachmentFile=this_file,
            AttachmentType=self.request.form.get('AttachmentType', ''),
            AttachmentKeys=self.request.form['AttachmentKeys'])
        attachment.processForm()
        attachment.reindexObject()

        other_attachs = self.context.getAttachment()
        attachments = []
        for other in other_attachs:
            attachments.append(other.UID())
        attachments.append(attachment.UID())

        self.context.setAttachment(attachments)

        self.request.RESPONSE.redirect(self.context.absolute_url())

    def getAttachments(self):
        attachments = []
        kit_atts = self.context.getAttachment()
        for att in kit_atts:
            file = att.getAttachmentFile()
            fsize = file.getSize() if file else 0
            if fsize < 1024:
                fsize = '%s b' % fsize
            else:
                fsize = '%s Kb' % (fsize / 1024)
            attachments.append({
                'keywords': att.getAttachmentKeys(),
                'analysis': '',
                'size': fsize,
                'name': file.filename,
                'Icon': file.getBestIcon(),
                'type': att.getAttachmentType().Title() if
                att.getAttachmentType() else '',
                'absolute_url': att.absolute_url(),
                'UID': att.UID(),
            })
        return attachments

class KitBiospecimensView(BiospecimensView):
    """ Biospecimens veiw from kit view.
    """
    def __init__(self, context, request):
        BiospecimensView.__init__(self, context, request)
        self.context = context
        self.context_actions = {}

        # Filter biospecimens by project uid
        self.columns.pop('Project', None)
        # path = '/'.join(self.context.getPhysicalPath())
        for state in self.review_states:
            # state['contentFilter']['path'] = {'query': path, 'depth': 1}
            state['contentFilter']['getProjectUID'] = self.context.aq_parent.UID()
            state['contentFilter']['sort_on'] = 'sortable_title'
            state['columns'].remove('Project')

    def folderitems(self, full_objects=False):
        items = BiospecimensView.folderitems(self)
        out_items = []
        for item in items:
            if "obj" not in item:
                continue
            obj = item['obj']
            kit = obj.getField('Kit').get(obj)
            if kit:
                kit_uid = kit.UID()
                if kit_uid == self.context.UID():
                    out_items.append(item)
        return out_items

class PrintView(KitView):
    template = ViewPageTemplateFile('templates/print.pt')
    _TEMPLATES_DIR = 'templates/print'

    def __call__(self):
        self.kit_name = self.context.getKitTemplate().Title()
        # self.quantity = self.context.getQuantity()
        items = self.context.getKitTemplate().kittemplate_lineitems
        self.items = []
        for item in items:
            product_title = item['title']
            price = float(item['price'])
            vat = float(item['VAT'])
            qty = float(item['quantity'])
            self.items.append({
                'title': product_title,
                'price': price,
                'vat': vat,
                'quantity': qty,
                'totalprice': '%.2f' % (price * qty)
            })
        self.items = sorted(self.items, key=itemgetter('title'))
        self.subtotal = '%.2f' % self.context.getKitTemplate().getSubtotal()
        self.vat = '%.2f' % self.context.getKitTemplate().getVATAmount()
        self.total = '%.2f' % float(self.context.getKitTemplate().getTotal())
        return self.template()

    def getCSS(self):
        template_name = 'kit_print.pt'
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
        path = '%s/%s.css' % (templates_dir, template_name[:-3])
        with open(path, 'r') as content_file:
            content = content_file.read()

        return content

    def renderKTemplate(self):
        templates_dir = self._TEMPLATES_DIR
        template_name = 'kit_print.pt'

        embed = ViewPageTemplateFile(os.path.join(templates_dir, template_name))
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except:
            tbex = traceback.format_exc()
            ktid = self.context.id
            reptemplate = "<div class='error-print'>%s - %s " \
                          "'%s':<pre>%s</pre></div>" % (
                ktid, _("Unable to load the template"), template_name, tbex)

        return reptemplate

    def getKitInfo(self):
        data = dict()
        data['date_printed'] = self.ulocalized_time(DateTime(), long_format=1)
        data['date_created'] = self.ulocalized_time(self.context.created(), long_format=1)
        data['createdby'] = _createdby_data(self)
        data['printedby'] = _printedby_data(self)
        data['laboratory'] = _lab_data(self)

        return data
