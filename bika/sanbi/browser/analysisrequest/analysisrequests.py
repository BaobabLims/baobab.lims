from bika.lims.browser.client import ClientAnalysisRequestsView


class AnalysisRequestsView(ClientAnalysisRequestsView):
    """List all created ARs
    """
    def __init__(self, context, request):
        ClientAnalysisRequestsView.__init__(self, context, request)
        self.catalog = "bika_catalog"
        path = '/'.join(self.context.getPhysicalPath())
        self.contentFilter = {
            'portal_type': 'AnalysisRequest',
            'sort_on': 'created',
            'sort_order': 'reverse',
            'cancellation_state': 'active',
        }

        cols = [
            'getDateSampled', 'getSampler', 'getDatePreserved',
            'getPreserver', 'getProfilesTitle', 'getTemplateTitle',
            'getDateSampled', 'AdHoc', 'SamplingDeviation',
            'getClientReference', 'getClientSampleID', 'BatchID'
        ]
        for col in self.columns.keys():
            if col in cols:
                del self.columns[col]

        ids = [
            'to_be_sampled', 'to_be_preserved', 'scheduled_sampling',
            'invalid', 'assigned', 'unassigned', 'rejected'
        ]
        j = 0
        for i in range(len(self.review_states)):
            if i - j > len(self.review_states): break
            if self.review_states[i - j]['id'] in ids:
                self.review_states.pop(i-j)
                j += 1
                continue
            k = 0
            for c in range(len(self.review_states[i-j]['columns'])):
                if c - k > len(self.review_states[i-j]['columns']):
                    break
                if self.review_states[i-j]['columns'][c-k] in cols:
                    self.review_states[i-j]['columns'].pop(c-k)
                    k += 1
