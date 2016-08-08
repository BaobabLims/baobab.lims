from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims import PMF
from bika.lims.workflow import doActionFor

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

    def workflow_action_complete(self):
        form = self.request.form

        selected_biospecimens = WorkflowAction._get_selected_items(self)
        biospecimens = []
        if form['Barcode']:
            barcode_dict = dict(form['Barcode'][0])
            for uid, barcode in barcode_dict.iteritems():
                biospecimen = selected_biospecimens.get(uid, None)
                if biospecimen:
                    biospecimen.setBarcode(barcode)
                    biospecimens.append(biospecimen)
                else:
                    continue


            message = PMF("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')

        for biospecimen in biospecimens:
            doActionFor(biospecimen, 'complete')
        self.destination_url = self.context.absolute_url()
        self.request.response.redirect(self.destination_url)