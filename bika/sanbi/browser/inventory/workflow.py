from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.utils import isActive

import plone


class OrderWorkflowAction(WorkflowAction):

    """Workflow actions taken in Order context.

    """

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        if type(action) in (list, tuple):
            action = action[0]
        if type(came_from) in (list, tuple):
            came_from = came_from[0]
        # Call out to the workflow action method
        # Use default bika_listing.py/WorkflowAction for other transitions
        method_name = 'workflow_action_' + action
        method = getattr(self, method_name, False)
        if method:
            method()
        else:
            WorkflowAction.__call__(self)

    def workflow_action_dispatch(self):
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        if not isActive(self.context):
            message = _('Item is inactive.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())
            return
        # Order publish preview
        self.request.response.redirect(self.context.absolute_url() + "/publish")
