from DateTime import DateTime
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

    def kits(self):
        """ Return only project's kits with status generated and active
        """
        items = []
        w_tool = getToolByName(self.context, 'portal_workflow')
        kits = self.context.objectValues('Kit')
        # import pdb;pdb.set_trace()
        for kit in kits:
            st1 = w_tool.getStatusOf("bika_kit_assembly_workflow", kit)
            st2 = w_tool.getStatusOf("bika_inactive_workflow", kit)
            if st1.get('review_state', None) == 'generated' and \
                            st2.get('inactive_state', None) == 'active':
                items.append({'uid':kit.UID(), 'title':kit.Title()})
        items.sort(lambda x, y: cmp(x['title'], y['title']))

        return items

    def render(self):
        if self.request.URL.endswith('biospecimens'):
            return self.index()
        else:
            return ''


class AddBiospecimensSubmitHandler(BrowserView):
    """
    """
    def __call__(self):
        # import pdb;pdb.set_trace()
        if "viewlet_submitted" in self.request.form:
            data = {}
            try:
                data = self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)

            # Validation is complete, now set local variables from form inputs.

            biospecimens = []
            j = 0
            if data:
                for x in range(data['seq_start'], data['seq_start'] + data['biospecimen_count']):
                    obj = api.content.create(
                        container=self.context,
                        type='Biospecimen',
                        id=data['id_template'].format(id=x),
                        title=data['title_template'].format(id=x),
                        DateCreated = DateTime()
                    )
                    obj.setKit(data['kits'][j].UID())
                    # obj.setType(data['type_uid'])
                    self.context.manage_renameObject(obj.id, data['id_template'].format(id=x), )
                    obj.reindexObject(idxs=['biospecimen_kit_uid'])
                    if (x-data['seq_start']+1) % data['biospecimen_per_kit'] == 0 and (x-data['seq_start']+1) != 0:
                        j += 1

                    biospecimens.append(obj)

                msg = u'%s Biospecimens created.' % len(biospecimens)
                self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def kits_between_limits(self, first_limit_uid, last_limit_uid):
        """Retrieve kits between the two limits
        """
        w_tool = getToolByName(self.context, 'portal_workflow')
        uc = getToolByName(self.context, 'uid_catalog')
        first_kit_id = uc(UID=first_limit_uid)[0].id
        last_kit_id = uc(UID=last_limit_uid)[0].id
        p_kits = self.context.objectValues('Kit')
        # Filter kits by workflow state active
        kits = []
        for kit in p_kits:
            st1 = w_tool.getStatusOf("bika_kit_assembly_workflow", kit)
            st2 = w_tool.getStatusOf("bika_inactive_workflow", kit)
            if st1.get('review_state', None) == 'generated' and \
                    st2.get('inactive_state', None) == 'active' and \
                        first_kit_id <= kit.getId() <= last_kit_id:
                kits.append(kit)

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

        first_kit_limit = form.get('first_kit_limit', None)
        last_kit_limit = form.get('last_kit_limit', None)
        if not first_kit_limit or not last_kit_limit:
            raise ValidationError(u'Kits range is required. Or project select has no kits!')

        kits = self.kits_between_limits(first_kit_limit, last_kit_limit)
        count = len(kits)
        biospecimen_per_kit = int(form.get('biospecimen_per_kit', None))
        biospecimen_count = count * biospecimen_per_kit

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues()]
        for x in range(biospecimen_count):
            check = id_template.format(id=seq_start + x)
            if check in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % check)

        return {
            'title_template': title_template,
            'id_template': id_template,
            'seq_start': seq_start,
            'first_kit_limit': first_kit_limit,
            'last_kit_limit': last_kit_limit,
            'kits': kits,
            'biospecimen_per_kit': biospecimen_per_kit,
            'biospecimen_count': biospecimen_count
        }

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())
