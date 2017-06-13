from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from Products.CMFCore.utils import getToolByName
from zope.schema import ValidationError
from DateTime import DateTime


class AddAliquotsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_aliquots_viewlet.pt")

    # TODO: Redundant code! This method also created in add_biospecimens_viewlet.py?
    def get_biospecimen_types(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title) \
                 for c in bsc(portal_type='BiospecType',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items

    def render(self):
        return self.index()


class AddAliquotsSubmitHandler(BrowserView):
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
            aliquots = []
            j = 0
            for x in range(data['seq_start'], data['seq_start'] + data['count']):
                obj = api.content.create(
                    container=self.context,
                    id=data['id_template'].format(id=x),
                    title=data['title_template'].format(id=x),
                    type='Aliquot',
                    DateCreated=DateTime()
                )

                # obj.setAliquotType(data['aliquot_type_uid'])
                obj.setBiospecimen(data['biospecimens'][j].UID)
                self.context.manage_renameObject(obj.id, data['id_template'].format(id=x), )
                obj.reindexObject()
                if (x-data['seq_start']+1) % data['aliquot_count'] == 0 and (x-data['seq_start']+1) != 0:
                    j += 1
                aliquots.append(obj)

            msg = u'%s Aliquots created.' % len(aliquots)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def bio_between_limits(self, first_limit_uid, last_limit_uid, project_uid):

        bc = getToolByName(self.context, 'bika_catalog')
        uc = getToolByName(self.context, 'uid_catalog')
        first_bio_id = uc(UID=first_limit_uid)[0].id
        last_bio_id = uc(UID=last_limit_uid)[0].id
        kit_brains = bc(portal_type='Kit', inactive_state='active', kit_project_uid=project_uid)
        biospecimens = []
        for brain in kit_brains:
            bio_brains = bc(portal_type='Biospecimen', inactive_state='active', biospecimen_kit_uid=brain.UID)
            biospecimens.extend([b for b in bio_brains])

        # TODO: Try to remove elements from biospecimens instead of using a new list bios?
        bios = []
        for biospecimen in biospecimens:
            if biospecimen.id >= first_bio_id and biospecimen.id <= last_bio_id:
                bios.append(biospecimen)

        return bios

    def validate_form_inputs(self):
        """Validate form inputs
        """
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

        first_bio_limit = form.get('first_biosepcimen_limit', None)
        last_bio_limit = form.get('last_biospecimen_limit', None)
        if not first_bio_limit or not last_bio_limit:
            raise ValidationError(u'Kits range is required. Or project select has no kits!')

        biospecimens = self.bio_between_limits(first_bio_limit, last_bio_limit, project_uid)
        bio_count = len(biospecimens)
        aliquot_count = int(form.get('aliquot_count', None))
        count = bio_count * aliquot_count

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues('Aliquot')]
        for x in range(count):
            check = id_template.format(id=seq_start + x)
            if check in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % check)

        return {
            'title_template': title_template,
            'id_template': id_template,
            'seq_start': seq_start,
            'project_uid': project_uid,
            'first_bio_limit': first_bio_limit,
            'last_bio_limit': last_bio_limit,
            'biospecimens': biospecimens,
            'count': count,
            'aliquot_count': aliquot_count,
        }

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())
