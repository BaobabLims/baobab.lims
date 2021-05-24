from baobab.lims.utils.retrieve_objects import get_object_from_uid

class ModifiedVirusSample:

    # def __init__(self):
        # super.__init__(self)

    def modify_return_type(self, info):
        info['disease_ontology_title'] = self.get_disease_title(info['DiseaseOntology']['uid'])
        # info['diease_ontology_title'] = 'This is a test disease'
        return info

    def get_disease_title(self, uid):
        try:
            return get_object_from_uid(uid).Title()
        except:
            return ''
