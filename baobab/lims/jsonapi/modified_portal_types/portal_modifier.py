from baobab.lims.jsonapi.modified_portal_types.virus_sample import ModifiedVirusSample


class ModifierFactory:
    def get_portal_type_modifier(self, portal_type):

        if portal_type == 'VirusSample':
            return ModifiedVirusSample()
        else:
            raise Exception('The specified portal type doesnt have a modifier.')
