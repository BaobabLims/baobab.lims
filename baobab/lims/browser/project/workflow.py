from bika.lims.browser.bika_listing import WorkflowAction
from baobab.lims.browser.biospecimen.workflow import BiospecimenWorkflowAction
import plone

# class ProjectWorkflowAction(WorkflowAction, BiospecimenWorkflowAction):
class ProjectWorkflowAction(WorkflowAction):

    def __call__(self):

        print('===========Inside project call')

        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        action, _ = WorkflowAction._get_form_workflow_action(self)
        if action == 'receive' and 'Type' in form:
            BiospecimenWorkflowAction.__call__(self)
        else:
            WorkflowAction.__call__(self)

    def workflow_action_finalise(self):
        print('------This is finalise workflow')