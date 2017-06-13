from bika.lims.browser.analysisrequest import AnalysisRequestsView as ARV
from baobab.lims.browser.analysisrequest import hide_actions_and_columns


class AnalysisRequestsView(ARV):
    """List all created ARs
    """
    def __init__(self, context, request):
        ARV.__init__(self, context, request)
        self.catalog = "bika_catalog"
        path = '/'.join(self.context.getPhysicalPath())
        self.contentFilter = {
            'portal_type': 'AnalysisRequest',
            'sort_on': 'created',
            'sort_order': 'reverse',
            'cancellation_state': 'active',
        }
        hide_actions_and_columns(self)

    def __call__(self):
        return ARV.__call__(self)
