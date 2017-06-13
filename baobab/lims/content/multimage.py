from zope.interface import implements
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from baobab.lims.interfaces import IMultimage
from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from DateTime import DateTime
from plone.formwidget.datetime.at import DatetimeWidget

from Products.validation import V_REQUIRED
from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.Archetypes.atapi import ImageField
from Products.Archetypes.atapi import ImageWidget
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.Archetypes.atapi import PrimaryFieldMarshaller


schema = BikaSchema.copy() + atapi.Schema((
    atapi.StringField('DocumentID',
        required=1,
        validators=('uniquefieldvalidator',),
        widget=atapi.StringWidget(
            label=_("Document ID"),
            visible={'view': 'visible', 'edit': 'visible'},
        )),

    atapi.StringField('SmallDescription',
        widget=atapi.StringWidget(
            label=_("Small Description"),
            visible={'view': 'visible', 'edit': 'visible'},
        )
        ),

    # atapi.FileField('File',
    #     required=1,
    #     widget=atapi.FileWidget(
    #         label=_("Document"),
    #         description=_("File upload "),
    #     )),

    ImageField('File',
        required=True,
        primary=True,
        languageIndependent=True,
        storage=AnnotationStorage(migrate=True),
        swallowResizeExceptions=zconf.swallowImageResizeExceptions.enable,
        pil_quality=zconf.pil_config.quality,
        pil_resize_algo=zconf.pil_config.resize_algo,
        max_size=zconf.ATImage.max_image_dimension,
        sizes={'large': (768, 768),
              'preview': (400, 400),
              'mini': (200, 200),
              'thumb': (128, 128),
              'tile': (64, 64),
              'icon': (32, 32),
              'listing': (16, 16),
              },
        validators=(('isNonEmptyFile', V_REQUIRED),
                   ('checkImageMaxSize', V_REQUIRED)),
        widget=ImageWidget(
            description='',
            label=_(u'label_image', default=u'Image'),
            show_content_type=False,
            visible={'view': 'visible', 'edit': 'visible'},
        )),

    atapi.DateTimeField('DatetimeCreated',
        default_method=DateTime,
        widget=atapi.CalendarWidget(
            label='Date/Time Creation',
            description='Select the date and time the photo of the biospecimen is taken.',
            ampm=1,
            visible={'view': 'visible', 'edit': 'visible'},
        )),
), marshall=PrimaryFieldMarshaller())

title = schema['title']
title.required = 0
title.widget.visible = False

class Multimage(BaseContent):
    implements(IMultimage)
    schema = schema

    security = ClassSecurityInfo()

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """
        """
        f = self.getPrimaryField()
        if f is None:
            return 0
        return f.get_size(self) or 0

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('File').tag(self, **kwargs)

    def __str__(self):
        """cmf compatibility
        """
        return self.tag()

    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the file (use default index_html)
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getPrimaryField()
        return field.download(self, REQUEST, RESPONSE)

# Activating the content type in Archetypes' internal types registry
atapi.registerType(Multimage, config.PROJECTNAME)