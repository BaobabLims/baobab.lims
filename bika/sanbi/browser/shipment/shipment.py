from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter, methodcaller
from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from Products.ATContentTypes.lib import constraintypes
from Products.CMFPlone.utils import _createObjectByType
from Products.Archetypes.public import BaseFolder
from DateTime import DateTime
from bika.lims.utils import to_utf8
import os
import traceback


class ShipmentView(BrowserView):

    template = ViewPageTemplateFile('templates/shipment_view.pt')
    title = _("Shipment Info")

    def __call__(self):

        context = self.context
        portal = self.portal

        self.absolute_url = context.absolute_url()
        setup = portal.bika_setup
        # Disable the add new menu item
        #context.setConstrainTypesMode(1)
        #context.setLocallyAllowedTypes(())
        # Collect general data
        self.id = context.getId()
        self.title = context.Title()
        self.sender_address = context.getDeliveryAddress()
        self.header_text = "{0} : {1}".format(context.getProjectID(), context.getOwnShippingId())
        self.from_contact = context.getFromContact()
        self.to_contact = context.getToContact()
        self.study_name = context.getProjectID()
        kit = context.getKit()
        kit_template = kit.getKitTemplate()
        self.kit_name = kit_template.Title()
        self.kit_quantity = kit_template.getQuantity()
        self.kit_assembled_date = kit.CreationDate()
        self.kit_expiration_date = self.ulocalized_time(kit.getExpiryDate())

        self.date_dispatched = self.ulocalized_time(context.getDateDispatched())
        self.courier_name = context.getCourier().Title()

        self.user = context.getOwner()


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
        ships = attachment.aq_parent
        ids = [attachment.getId(), ]
        BaseFolder.manage_delObjects(ships, ids, self.request)

        #self.request.RESPONSE.redirect(self.context.absolute_url())
        self.request.RESPONSE.redirect(self.request.REQUEST.get_header('referer'))

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()

    def addShipAttachment(self, REQUEST=None, RESPONSE=None):
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
        ship_atts = self.context.getAttachment()
        for att in ship_atts:
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

    template = ViewPageTemplateFile('templates/shipment_edit.pt')
    field = ViewPageTemplateFile('templates/row_field.pt')

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup

        if 'submitted' in request:
            #pdb.set_trace()
            context.setConstrainTypesMode(constraintypes.DISABLED)
            # This following line does the same as precedent which one is the best?
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


class PrintView(ShipmentView):

    template = ViewPageTemplateFile('templates/print.pt')
    _TEMPLATES_DIR = 'templates/print'

    def __call__(self):

        context = self.context
        portal = self.portal

        self.absolute_url = context.absolute_url()
        setup = portal.bika_setup
        # Disable the add new menu item
        #context.setConstrainTypesMode(1)
        #context.setLocallyAllowedTypes(())
        # Collect general data
        self.id = context.getId()
        self.title = context.Title()
        self.sender_address = context.getDeliveryAddress()
        self.header_text = "{0} : {1}".format(context.getProjectID(), context.getOwnShippingId())
        self.from_contact = context.getFromContact()
        self.to_contact = context.getToContact()
        self.study_name = context.getProjectID()
        kit = context.getKit()
        kit_template = kit.getKitTemplate()
        self.kit_name = kit_template.Title()
        self.kit_quantity = kit_template.getQuantity()
        self.kit_assembled_date = kit.CreationDate()
        self.kit_expiration_date = self.ulocalized_time(kit.getExpiryDate())

        self.date_dispatched = self.ulocalized_time(context.getDateDispatched())
        self.courier_name = context.getCourier().Title()

        self.user = context.getOwner()


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
        self.header_text = "{0} : {1}".format(self.context.getProjectID(), self.context.getOwnShippingId())
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