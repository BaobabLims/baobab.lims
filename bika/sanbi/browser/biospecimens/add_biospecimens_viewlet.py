from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.schema import ValidationError
from Products.CMFCore.utils import getToolByName


class AddBiospecimensViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_biospecimens_viewlet.pt")

    def get_biospecimen_types(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title) \
                 for c in bsc(portal_type='BiospecType',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items

    def render(self):
        return self.index()


class AddBiospecimensSubmitHandler(BrowserView):
    """
    """
    def __call__(self):

        if "viewlet_submitted" in self.request.form:
            data = {}
            try:
                data = self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)

            # Validation is complete, now set local variables from form inputs.

            biospecimens = []
            j = 0
            for x in range(data['seq_start'], data['seq_start'] + data['biospecimen_count']):
                obj = api.content.create(
                    container=self.context,
                    type='Biospecimen',
                    id=data['id_template'].format(id=x),
                    title=data['title_template'].format(id=x),
                    SubjectID=data['subject_id'],
                    Barcode='',
                    Volume=data['volume'],
                    Unit=data['volume_unit']
                    # Kit=data['kits'][j].getObject()
                )
                obj.setKit(data['kits'][j].UID)
                obj.setType(data['type_uid'])
                self.context.manage_renameObject(obj.id, data['id_template'].format(id=x), )
                obj.reindexObject(idxs=['biospecimen_kit_uid'])
                if (x-data['seq_start']+1) % data['biospecimen_per_kit'] == 0 and (x-data['seq_start']+1) != 0:
                    j += 1

                biospecimens.append(obj)



            msg = u'%s Biospecimens created.' % len(biospecimens)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def kits_between_limits(self, first_limit_uid, last_limit_uid, project_uid):
        """Retrieve kits between the two limits
        """
        bc = getToolByName(self.context, 'bika_catalog')
        uc = getToolByName(self.context, 'uid_catalog')
        first_kit_id = uc(UID=first_limit_uid)[0].id
        last_kit_id = uc(UID=last_limit_uid)[0].id
        brains = bc(portal_type='Kit', inactive_state='active', kit_project_uid=project_uid)
        kits = []
        for brain in brains:
            if brain.id >= first_kit_id and brain.id <= last_kit_id:
                kits.append(brain)

        return kits

    def validate_form_inputs(self):

        form = self.request.form

        title_template = form.get('titletemplate', None)
        id_template = form.get('idtemplate', None)
        if not (title_template and id_template):
            raise ValidationError(u'ID and Title template are both required.')
        if not ('{id}' in title_template and '{id}' in id_template):
            raise ValidationError(u'ID and Title templates must contain {id} '
                                  u'for ID sequence substitution')

        try:
            seq_start = int(form.get('seq_start', None))
        except:
            raise ValidationError(
                u'Sequence start and all counts must be integers')

        project_uid = form.get('Project_uid', None)
        if not project_uid:
            raise ValidationError(u'Project is required and should be not "None"')

        first_kit_limit = form.get('first_kit_limit', None)
        last_kit_limit = form.get('last_kit_limit', None)
        if not first_kit_limit or not last_kit_limit:
            raise ValidationError(u'Kits range is required. Or project select has no kits!')

        kits = self.kits_between_limits(first_kit_limit, last_kit_limit, project_uid)
        count = len(kits)
        biospecimen_per_kit = int(form.get('biospecimen_per_kit', None))
        biospecimen_count = count * biospecimen_per_kit

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues('Kit')]
        for x in range(biospecimen_count):
            check = id_template.format(id=seq_start + x)
            if check in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % check)

        biospecimen_type = form.get('biospecimen_type', None)
        if not biospecimen_type or biospecimen_type == 'None':
            raise ValidationError(u'Biospecimen type is required and should be not "None"')

        volume_unit = form.get('volume_unit', None)
        volume = form.get('biospecimen_volume', None)
        if not volume or volume <= 0:
            raise ValidationError(u'Biospecimen volume is required and should not be positive.')

        subject_id = form.get('subject_id', None)
        if not subject_id:
            raise ValidationError(u'Subject ID is required.')

        return {
            'title_template': title_template,
            'id_template': id_template,
            'seq_start': seq_start,
            'project_uid': project_uid,
            'first_kit_limit': first_kit_limit,
            'last_kit_limit': last_kit_limit,
            'kits': kits,
            'biospecimen_per_kit': biospecimen_per_kit,
            'biospecimen_count': biospecimen_count,
            'type_uid': biospecimen_type,
            'volume': volume,
            'volume_unit': volume_unit,
            'subject_id': subject_id
        }

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())