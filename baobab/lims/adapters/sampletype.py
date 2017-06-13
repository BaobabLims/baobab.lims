from zope.component import adapts
from zope.interface import implements

from bika.lims.interfaces import IJSONReadExtender
from bika.lims.interfaces import ISampleType


class JSONReadExtender(object):
    """- Place additional information about profile services
    into the returned records.
    Used in AR Add to prevent extra requests
    """

    implements(IJSONReadExtender)
    adapts(ISampleType)

    def __init__(self, context):
        self.context = context

    def __call__(self, request, data):
        service_data = []
        field = self.context.getField('Service')
        services = field.getAccessor(self.context)()
        for service in services:
            this_service = {
                'UID': service.UID(),
                'Title': service.Title(),
                'Keyword': service.getKeyword(),
                'Price': service.getPrice(),
                'VAT': service.getVAT(),
                'PointOfCapture': 'analyses',
                'CategoryTitle': service.getCategory().Title()
            }
            service_data.append(this_service)
        data['service_data'] = service_data
