from datetime import datetime
from DateTime import DateTime

from bika.lims.jsonapi.interfaces import IBatch
from bika.lims import api as bika_lims_api
from Products.CMFPlone.PloneBatch import Batch


class ModifiedVirusSample:

    def modify_return_type(self, info):
        info['disease_title'] = ''
        try:
            virus_sample = self.get_object_by_uid(info['uid'])
            info['baobab_modified_at'] = self.get_iso_date(virus_sample.getField('modification_date').get(virus_sample))
            info['baobab_created_at'] = self.get_iso_date(virus_sample.getField('creation_date').get(virus_sample))

            disease = info['HostDisease']
            disease_uid = disease['uid']
            info['disease_title'] = self.get_disease_title(disease_uid)
        except:
            pass

        return info

    def get_disease_title(self, uid):

        try:
            obj = self.get_object_by_uid(uid)
            return obj.Title()
        except Exception as e:
            return ''

    def get_iso_date(self, virus_sample_date):
        python_date = virus_sample_date.asdatetime()
        iso_format = python_date.isoformat()
        return iso_format

    def get_object_by_uid(self, uid, default=None):
        """Proxy to bika.lims.api.get_object_by_uid
        """
        return bika_lims_api.get_object_by_uid(uid, default)

    def get_batch_on_datetime(self, sequence, last_modified_date):

        new_batch = []
        for element in sequence:
            virus_sample = element.getObject()
            object_modifed_date = virus_sample.getField('modification_date').get(virus_sample)
            python_dt = object_modifed_date.asdatetime()
            iso_object_modified_date = python_dt.isoformat()

            if not last_modified_date or iso_object_modified_date > last_modified_date:
                new_batch.append(virus_sample)

        return self.make_batch(new_batch)

    def make_batch(self, sequence):
        start = 0
        return IBatch(Batch(sequence, len(sequence)), start)
