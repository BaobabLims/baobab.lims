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

    def __call__(self):

        context = self.context
        portal = self.portal

        self.absolute_url = context.absolute_url()
        setup = portal.bika_setup
        # Disable the add new menu item
        context.setConstrainTypesMode(1)
        context.setLocallyAllowedTypes(())
        # Collect general data
        self.id = context.getId()
        self.title = context.Title()

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

    def addShipmentAttachment(self, REQUEST=None, RESPONSE=None):
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

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup

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

