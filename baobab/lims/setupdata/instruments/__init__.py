from bika.lims.exportimport import instruments
from biorad.tc20 import tc20

import inspect
import sys

__all__ = instruments.__all__
__all__.append('biorad.tc20.tc20')

def getExim(exim_id):
    if exim_id == 'biorad.tc20.tc20':
        currmodule = sys.modules[__name__]
        members = [obj for name, obj in inspect.getmembers(currmodule) \
                   if hasattr(obj, '__name__') \
                   and obj.__name__.endswith(exim_id)]
        return members[0] if len(members) > 0 else None
    else:
        return instruments.getExim(exim_id)