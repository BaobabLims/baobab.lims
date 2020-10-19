from Products.Archetypes.exceptions import ReferenceException

from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims import PMF
from bika.lims.workflow import doActionFor
from baobab.lims.config import VOLUME_UNITS

import plone

class BiospecimenWorkflowAction(WorkflowAction):

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        action, _ = WorkflowAction._get_form_workflow_action(self)
        if type(action) in (list, tuple):
            action = action[0]

        # Call out to the workflow action method
        method_name = 'workflow_action_' + action
        method = getattr(self, method_name, False)
        if method:
            method()
        else:
            WorkflowAction.__call__(self)

    def workflow_action_receive(self):
        form = self.request.form
        # print form
        selected_biospecimens = WorkflowAction._get_selected_items(self)
        biospecimens = []
        for uid in selected_biospecimens.keys():
            if not form['Volume'][0][uid] or \
                    not form['Unit'][0][uid] or \
                    not form['SubjectID'][0][uid]:
                continue

            try:
                obj = selected_biospecimens.get(uid, None)
                obj.getField('Volume').set(obj, form['Volume'][0][uid])
                obj.getField('SubjectID').set(obj, form['SubjectID'][0][uid])
                if 'Unit' in form and form['Unit'][0][uid]:
                    obj.getField('Unit').set(obj, form['Unit'][0][uid])
                location = obj.getStorageLocation()
                if location:
                    doActionFor(location, 'occupy')

                obj.reindexObject()
                biospecimens.append(obj)
            except ReferenceException:
                continue

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')

        for biospecimen in biospecimens:
            doActionFor(biospecimen, 'receive')
            for partition in biospecimen.objectValues('SamplePartition'):
                doActionFor(partition, 'receive')

        self.destination_url = self.context.absolute_url()
        if form['portal_type'] == 'Kit' or \
                form['portal_type'] == 'SampleBatch':
            self.destination_url = form['view_url']

        self.destination_url += '/biospecimens'
        self.request.response.redirect(self.destination_url)

    def workflow_action_sample_due(self):
        form = self.request.form
        selected_biospecimens = WorkflowAction._get_selected_items(self)
        biospecimens = []
        for uid in selected_biospecimens.keys():
            if not form['Barcode'][0][uid] or \
                    not form['Type'][0][uid]:
                continue
            try:
                obj = selected_biospecimens.get(uid, None)
                obj.getField('Barcode').set(obj, form['Barcode'][0][uid])
                obj.getField('SampleType').set(obj, form['Type'][0][uid])
                obj.setId(form['Barcode'][0][uid])
                obj.edit(SampleID=obj.getId())
                obj.reindexObject()
                biospecimens.append(obj)
            except ReferenceException:
                continue
        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')

        for biospecimen in biospecimens:
            doActionFor(biospecimen, 'sample_due')
            for partition in biospecimen.objectValues('SamplePartition'):
                doActionFor(partition, 'sample_due')

        self.destination_url = self.context.absolute_url()
        if form['portal_type'] == 'Kit' or \
                form['portal_type'] == 'SampleBatch':
            self.destination_url = form['view_url']

        self.destination_url += '/biospecimens'
        self.request.response.redirect(self.destination_url)
