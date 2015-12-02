from bika.health import bikaMessageFactory as _
from bika.health.browser.doctors.folder_view import DoctorsView as _dv

# See ./configure.zcml


class DoctorsView(_dv):

    def __init__(self, context, request):
        super(DoctorsView, self).__init__(context, request)

        # Add new column definitions
        self.columns.extend({
            'AFerret': {'title': _('A Ferret')},
            'AField': {'title': _('A Field')},
        })

        # all dicts in self.review_states have a list of columns,
        # which we must update.  We will choose to show the new
        # fields in all filter states:
        for i in len(self.review_states):
            self.review_states[i]['columns'].append('AFerret', 'AField')

    def folderitems(self):
        items = super(DoctorsView, self).folderitems()
        for i in range(len(items)):
            if 'obj' not in items[i]:
                # skip over items that are not part of
                # the current page
                continue
            obj = items[i]['obj']
            items[i]['AFerret'] = obj.schema['Ferret'].get(obj)
            items[i]['AField'] = obj.schema['Field'].get(obj)

        return items
