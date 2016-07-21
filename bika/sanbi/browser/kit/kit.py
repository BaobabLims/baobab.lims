from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter
from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from Products.ATContentTypes.lib import constraintypes
from Products.CMFPlone.utils import _createObjectByType
from Products.Archetypes.public import BaseFolder
from DateTime import DateTime
from bika.lims.utils import to_utf8
from Products.Archetypes.config import REFERENCE_CATALOG
import os
import traceback

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
                    "/++resource++bika.sanbi.images/inventory.png"
        self.id = context.getId()
        self.title = context.Title()
        self.kittemplate_title = context.getKitTemplate().Title()
        self.quantity = context.getQuantity()

        self.subtotal = '%.2f' % context.getKitTemplate().getSubtotal()
        self.vat = '%.2f' % context.getKitTemplate().getVATAmount()
        self.total = '%.2f' % float(context.getKitTemplate().getTotal())

        items = context.getKitTemplate().kittemplate_lineitems
        self.items = []
        for item in items:
            prodtitle = item['Product']
            price = float(item['Price'])
            vat = float(item['VAT'])
            qty = float(item['Quantity'])
            self.items.append({
                'title': prodtitle,
                'price': price,
                'vat': vat,
                'quantity': qty,
                'totalprice': '%.2f' % (price * qty)
            })
        self.items = sorted(self.items, key=itemgetter('title'))

        self.kit_storage = {
            'kitID': self.context.getId(),
            'stored': self.context.getQtyStored(),
            'qty': self.context.getQuantity(),
            'all_stored': self.context.getQuantity() == self.context.getQtyStored()
        }

        if 'form.action.addKitAttachment' in self.request:
            self.addKitAttachment()
        elif 'form.action.delARAttachment' in self.request:
            self.delARAttachment()

        # Render the template
        return self.template()

    def get_product_storage_qtts(self, uid):
        catalog = getToolByName(self.context, "bika_setup_catalog")
        brains = catalog({'portal_type': 'StorageInventory', 'inactive_state': 'active',
                          'object_provides': 'bika.sanbi.interfaces.IInventoryAssignable'})

        rc = getToolByName(self.context, REFERENCE_CATALOG)
        references = rc.getBackReferences(uid, relationship="StockItemProduct")
        stock_items = [ref.getSourceObject().getId() for ref in references if ref.getSourceObject().getIsStored()]

        ret = {}
        for brain in brains:
            ret[brain.title] = [brain.UID, 0]

        for si in stock_items:
            brains = catalog({'portal_type': 'StorageInventory',
                              'inactive_state': 'active',
                              'getISID': si})

            if brains:
                storage = brains[0].getObject().aq_parent
                ret[storage.title][1] += 1

        results = []
        for k in ret:
            results.append([k,ret[k]])

        return results

    def storage_products(self):
        results = []
        items = self.context.getKitTemplate().kittemplate_lineitems
        for item in items:
            storages = self.get_product_storage_qtts(item['UID'])
            results.append(([item['Product'], item['UID']], storages))

        return results


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

        #self.request.RESPONSE.redirect(self.context.absolute_url())
        self.request.RESPONSE.redirect(self.request.REQUEST.get_header('referer'))

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
                'type': att.getAttachmentType().Title() if att.getAttachmentType() else '',
                'absolute_url': att.absolute_url(),
                'UID': att.UID(),
            })
        return attachments


class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/kit_edit.pt')
    #field = ViewPageTemplateFile('templates/row_field.pt')

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup

        if 'submitted' in request:
            #pdb.set_trace()
            context.setConstrainTypesMode(constraintypes.DISABLED)
            # This following line does the same as the precedent. Which one is the best?
            #context.aq_parent.setConstrainTypesMode(constraintypes.DISABLED)
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return

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


class PrintView(KitView):

    template = ViewPageTemplateFile('templates/print.pt')
    _TEMPLATES_DIR = 'templates/print'

    def __call__(self):
        self.kit_name = self.context.getKitTemplate().Title()
        self.quantity = self.context.getQuantity()
        items = self.context.getKitTemplate().kittemplate_lineitems
        self.items = []
        self.items = []
        for item in items:
            prodtitle = item['Product']
            price = float(item['Price'])
            vat = float(item['VAT'])
            qty = float(item['Quantity'])
            self.items.append({
                'title': prodtitle,
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
            reptemplate = "<div class='error-print'>%s - %s '%s':<pre>%s</pre></div>" % (
            ktid, _("Unable to load the template"), template_name, tbex)

        return reptemplate

    def _createdby_data(self):
        """ Returns a dict that represents the user who created the ws
            Keys: username, fullmame, email
        """
        username = self.context.getOwner().getUserName()
        return {'username': username,
                'fullname': to_utf8(self.user_fullname(username)),
                'email': to_utf8(self.user_email(username))}

    def _printedby_data(self):
        """ Returns a dict that represents the user who prints the ws
            Keys: username, fullname, email
        """
        data = {}
        member = self.context.portal_membership.getAuthenticatedMember()
        if member:
            username = member.getUserName()
            data['username'] = username
            data['fullname'] = to_utf8(self.user_fullname(username))
            data['email'] = to_utf8(self.user_email(username))

            c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
                 if x.getObject().getUsername() == username]
            if c:
                sf = c[0].getObject().getSignature()
                if sf:
                    data['signature'] = sf.absolute_url() + "/Signature"

        return data

    def _lab_data(self):
        """ Returns a dictionary that represents the lab object
            Keys: obj, title, url, address, confidence, accredited,
                  accreditation_body, accreditation_logo, logo
        """
        portal = self.context.portal_url.getPortalObject()
        lab = self.context.bika_setup.laboratory
        lab_address = lab.getPostalAddress() \
                      or lab.getBillingAddress() \
                      or lab.getPhysicalAddress()
        if lab_address:
            _keys = ['address', 'city', 'state', 'zip', 'country']
            _list = ["<div>%s</div>" % lab_address.get(v) for v in _keys
                     if lab_address.get(v)]
            lab_address = "".join(_list)
        else:
            lab_address = ''

        return {'obj': lab,
                'title': to_utf8(lab.Title()),
                'url': to_utf8(lab.getLabURL()),
                'address': to_utf8(lab_address),
                'confidence': lab.getConfidence(),
                'accredited': lab.getLaboratoryAccredited(),
                'accreditation_body': to_utf8(lab.getAccreditationBody()),
                'accreditation_logo': lab.getAccreditationBodyLogo(),
                'logo': "%s/logo_print.png" % portal.absolute_url()}

    def getKitInfo(self):
        data = {
            'date_printed': self.ulocalized_time(DateTime(), long_format=1),
            'date_created': self.ulocalized_time(self.context.created(), long_format=1),
        }
        data['createdby'] = self._createdby_data()
        data['printedby'] = self._printedby_data()
        data['laboratory'] = self._lab_data()

        return data


class StoreKitAssembly:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        uc = getToolByName(self.context, 'uid_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        storage = uc(UID=form['StorageInventory_uid'])[0].getObject()
        brains = bsc(portal_type='StorageInventory', inactive_state='active',
                     path={'query': "/".join(storage.getPhysicalPath()), 'depth':1})

        brains = [brain for brain in brains if not brain.getObject().getIsOccupied()]
        message = ''
        number = int(form['number-kit'])
        if len(brains) < number:
            message = "No sufficient free positions availble."

        if message:
            self.context.plone_utils.addPortalMessage(_(message), 'error')
        else:
            positions = [brain.getObject() for brain in brains[:number]]
            product_uid = self.context.UID()
            references = rc.getBackReferences(product_uid, relationship="StockItemProduct")
            stock_items = [ref.getSourceObject() for ref in references if not ref.getSourceObject().getIsStored()]
            assert len(stock_items) >= len(positions)
            for i in range(len(positions)):
                position = positions[i]
                stock_item = stock_items[i]
                stock_item.setStorageLevelID(position.getId())
                stock_item.setIsStored(True)
                position.setISID(stock_item.getId())
                position.setIsOccupied(True)
                # Decrement number of available children of parent
                nac = position.aq_parent.getNumberOfAvailableChildren()
                position.aq_parent.setNumberOfAvailableChildren(nac - 1)
                # set number of kit stored
                self.context.setQtyStored(self.context.getQtyStored() + 1)

        self.request.response.redirect(self.context.absolute_url_path())
        return