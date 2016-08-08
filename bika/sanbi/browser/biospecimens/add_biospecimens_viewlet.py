from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.schema import ValidationError
from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName


class AddBiospecimensViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_biospecimens_viewlet.pt")

    def getBiospecimenTypes(self):
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
            try:
                self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)

            # Validation is complete, now set local variables from form inputs.
            form = self.request.form
            title_template = form.get('titletemplate', None)
            id_template = form.get('idtemplate', None)
            seq_start = int(form.get('seq_start', None))
            count = int(form.get('biospecimen_count', None))
            type_uid = form.get('biospecimen_type', None)
            biospecimen_per_kit = int(form.get('biospecimen_per_kit', None))
            volume = form.get('biospecimen_volume', None)
            volume_unit = form.get('volume_unit', None)
            subject_id = form.get('subject_id', None)
            barcodes = form.get('barcodes', None)
            if barcodes:
                barcodes = barcodes.split('\r\n')
            project_uid = form.get('Project_uid', None)
            # kits_range = form.get('kits_range', None)
            # min_range, max_range = map(int, kits_range.split('-'))

            bc = getToolByName(self.context, 'bika_catalog')
            # TODO: once kit workflow implemented, filter with kit state = received
            brains = bc(portal_type="Kit", inactive_state='active')
            kits = [brain.getObject() for brain in brains
                                      if brain.getObject().getProject().UID() == project_uid]

            # kits = kits[min_range:max_range]

            # assert len(kits) == count

            # assert len(barcodes) == count * biospecimen_per_kit

            biospecimens = []
            for x in range(seq_start, seq_start + count * biospecimen_per_kit):
                obj = api.content.create(
                    container=self.context,
                    type='Biospecimen',
                    id=id_template.format(id=x),
                    title=title_template.format(id=x),
                    SubjectID=subject_id,
                    Barcode='',
                    Volume=volume,
                    Unit=volume_unit
                )

                self.context.manage_renameObject(obj.id, id_template.format(id=x), )
                obj.setKit(kits[x - seq_start - (x-seq_start) % biospecimen_per_kit])
                obj.setType(type_uid)
                print obj.getType()
                biospecimens.append(obj)

            msg = u'%s Biospecimens created.' % len(kits)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())


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
            biospecimen_count = int(form.get('biospecimen_count', None))
        except:
            raise ValidationError(
                u'Sequence start and all counts must be integers')

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues('Kit')]
        for x in range(biospecimen_count):
            check = id_template.format(id=seq_start + x)
            if check in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % check)

        # Check the range of kits is correct
        # kits_range = form.get('kits_range', None)
        # if not kits_range:
        #     raise ValidationError(u'Kit int range is required.')
        # min, max = kits_range.split('-')
        # try:
        #     min = int(min)
        #     max = int(max)
        # except:
        #     raise ValidationError(
        #         u'Kits min and max range must be integers')

        # Biospecimen type is required and should be diffrent of None.
        biospecimen_type = form.get('sel_type', None)
        if not biospecimen_count or biospecimen_type == 'None':
            raise ValidationError(u'Biospecimen type is required and should be not "None"')

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())