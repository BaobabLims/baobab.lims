from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims import PMF
from bika.lims.workflow import doActionFor
from bika.sanbi.config import VOLUME_UNITS
from Products.Archetypes.exceptions import ReferenceException
import plone

class AliquotWorkflowAction(WorkflowAction):

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)

        action, _ = WorkflowAction._get_form_workflow_action(self)
        if type(action) in (list, tuple):
            action = action[0]

        # Call out to the workflow action method
        method_name = 'workflow_action_aliquot_' + action
        method = getattr(self, method_name, False)
        if method:
            method()
        else:
            WorkflowAction.__call__(self)

    def workflow_action_aliquot_receive(self):
        form = self.request.form
        selected_aliquots = WorkflowAction._get_selected_items(self)
        aliquots = []
        for uid in selected_aliquots.keys():
            if not form['AliquotType'][0][uid] or \
               not form['Volume'][0][uid] or \
               not form['Unit'][0][uid]:
                continue
            try:
                aliquot = selected_aliquots.get(uid, None)
                aliquot.getField('SampleType').set(aliquot, form['AliquotType'][0][uid])
                aliquot.getField('Volume').set(aliquot, form['Volume'][0][uid])
                unit = 'ml'
                for u in VOLUME_UNITS:
                    if u['ResultValue'] == form['Unit'][0][uid]:
                        unit = u['ResultText']
                aliquot.getField('Unit').set(aliquot, unit)
                aliquot.reindexObject()
                aliquots.append(aliquot)
            except ReferenceException:
                continue

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')

        for aliquot in aliquots:
            doActionFor(aliquot, 'receive')
            for partition in aliquot.objectValues('SamplePartition'):
                doActionFor(partition, 'receive')

        self.destination_url = self.context.absolute_url()
        if self.context.portal_type == 'Project':
            self.destination_url += '/aliquots'
        self.request.response.redirect(self.destination_url)