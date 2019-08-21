from DateTime import DateTime

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName

from bika.lims.utils import tmpID


class AuditLogger(object):

    def __init__(self, context, item_type='Sample'):
        self.context = context
        self._item_type = item_type

    def get_member(self):
        membership = getToolByName(self.context, 'portal_membership')
        if membership.isAnonymousUser():
            member = 'anonymous'
        else:
            member = membership.getAuthenticatedMember().getUserName()

        return member

    def perform_simple_audit(self,  changed_item=None, changed_field='New', old_value=None, new_value=None):
        audit_folder = self.context.auditlogs

        audit_object = _createObjectByType('AuditLog', audit_folder, tmpID())
        item_title = '%s Import' % self._item_type
        if changed_item:
            item_title = changed_item.Title()

        item_uid = 'N/A'
        if changed_item:
            item_uid = changed_item.UID()

        audit_object.edit(
            title='%s_%s' % (DateTime(), self.get_member()),
            AuditDate=DateTime(),
            AuditUser=self.get_member(),
            ItemType=self._item_type,
            ItemTitle=item_title,
            ItemUID=item_uid,
            ChangedValue=changed_field,
            OldValue=old_value,
            NewValue=new_value,
        )
        audit_object.reindexObject()

    def perform_reference_audit(self, changed_item, changed_field, old_reference, catalog, new_uid):

        audit_folder = self.context.auditlogs

        new_title = ''
        old_title = ''

        if new_uid:
            new_items_list = catalog(UID=new_uid)

            if new_items_list:
                new_item = new_items_list[0].getObject()
                new_title = new_item.Title()

        if old_reference:
            old_title = old_reference.Title()

        if old_title != new_title:

            audit_object = _createObjectByType('AuditLog', audit_folder, tmpID())
            audit_object.edit(
                title='%s_%s' % (DateTime(), self.get_member()),
                AuditDate=DateTime(),
                AuditUser=self.get_member(),
                ItemType=self._item_type,
                ItemTitle=changed_item.Title(),
                ItemUID=changed_item.UID(),
                ChangedValue=changed_field,
                OldValue=old_title,
                NewValue=new_title,
            )
            audit_object.reindexObject()

    def perform_multi_reference_audit(self, changed_item, changed_field, old_references, catalog, new_uids):

        audit_folder = self.context.auditlogs

        new_titles = self.get_new_references(new_uids, catalog)
        old_titles = self.get_old_references_list(old_references, catalog)

        if set(old_titles) != set(new_titles):
            audit_object = _createObjectByType('AuditLog', audit_folder, tmpID())
            audit_object.edit(
                title='%s_%s' % (DateTime(), self.get_member()),
                AuditDate=DateTime(),
                AuditUser=self.get_member(),
                ItemType=self._item_type,
                ItemTitle=changed_item.Title(),
                ItemUID=changed_item.UID(),
                ChangedValue=changed_field,
                OldValue=', '.join(old_titles),
                NewValue=', '.join(new_titles),
            )
            audit_object.reindexObject()

    def perform_multi_reference_list_to_list_audit(self, changed_item, changed_field, old_references, catalog, new_uids):

        audit_folder = self.context.auditlogs

        new_titles = self.get_new_references_list(new_uids, catalog)
        old_titles = self.get_old_references_list(old_references, catalog)

        if set(old_titles) != set(new_titles):
            audit_object = _createObjectByType('AuditLog', audit_folder, tmpID())
            audit_object.edit(
                title='%s_%s' % (DateTime(), self.get_member()),
                AuditDate=DateTime(),
                AuditUser=self.get_member(),
                ItemType=self._item_type,
                ItemTitle=changed_item.Title(),
                ItemUID=changed_item.UID(),
                ChangedValue=changed_field,
                OldValue=', '.join(old_titles),
                NewValue=', '.join(new_titles),
            )
            audit_object.reindexObject()

    def get_old_references_list(self, old_references, catalog):
        old_reference_titles = []

        for reference in old_references:

            items_list = []
            try:
                reference_title = reference.Title()
                old_reference_titles.append(reference_title)
            except AttributeError:
                if reference:
                    items_list = catalog(UID=reference)

                if items_list:
                    old_reference_titles.append(items_list[0].getObject().Title())

        return old_reference_titles


    def get_new_references_list(self, new_uids, catalog):

        new_references_titles = []

        for uid in new_uids:
            item_list = catalog(UID=uid)

            if item_list:
                new_references_titles.append(item_list[0].getObject().Title())

        return new_references_titles

    def get_new_references(self, new_uids, catalog):

        new_references_titles = []
        split_uids = new_uids.split(',')

        for uid in split_uids:
            item_list = catalog(UID=uid)

            if item_list:
                new_references_titles.append(item_list[0].getObject().Title())

        return new_references_titles





