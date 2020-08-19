import Products.ATExtensions
import Products.PloneTestCase.setup
import collective.js.jqueryui
import plone.app.iterate
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.setuphandlers import setupPortalContent
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import logout
from plone.testing import z2
from bika.lims.testing import getBrowser, RemoteKeywords
from plone.app.robotframework.remote import RemoteLibraryLayer
from plone.app.robotframework import AutoLogin, Content


class BaobabTestLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import bika.lims
        import baobab.lims
        import archetypes.schemaextender
        # Load ZCML
        self.loadZCML(package=Products.ATExtensions)
        self.loadZCML(package=plone.app.iterate)
        self.loadZCML(package=collective.js.jqueryui)
        self.loadZCML(package=archetypes.schemaextender)
        self.loadZCML(package=bika.lims)
        self.loadZCML(package=baobab.lims)

        # Required by Products.CMFPlone:plone-content
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'bika.lims')
        z2.installProduct(app, 'baobab.lims')

    def setUpPloneSite(self, portal):
        login(portal.aq_parent, SITE_OWNER_NAME)

        wf = getToolByName(portal, 'portal_workflow')
        wf.setDefaultChain('plone_workflow')
        setupPortalContent(portal)

        # make sure we have folder_listing as a template
        portal.getTypeInfo().manage_changeProperties(
            view_methods=['folder_listing'],
            default_view='folder_listing')

        applyProfile(portal, 'bika.lims:default')
        applyProfile(portal, 'baobab.lims:default')

        # Add some test users
        for role in ('LabManager',
                     'LabClerk',
                     'Analyst',
                     'Verifier',
                     'Sampler',
                     'Preserver',
                     'Publisher',
                     'Member',
                     'Reviewer',
                     'RegulatoryInspector'):
            for user_nr in range(2):
                if user_nr == 0:
                    username = "test_%s" % (role.lower())
                else:
                    username = "test_%s%s" % (role.lower(), user_nr)
                member = portal.portal_registration.addMember(
                    username,
                    username,
                    properties={
                        'username': username,
                        'email': username + "@example.com",
                        'fullname': username}
                )
                # Add user to all specified groups
                group_id = role + "s"
                group = portal.portal_groups.getGroupById(group_id)
                if group:
                    group.addMember(username)
                # Add user to all specified roles
                member._addRole(role)
                # If user is in LabManagers, add Owner local role on clients
                # folder
                if role == 'LabManager':
                    portal.clients.manage_setLocalRoles(username, ['Owner', ])

        ## load test data
        #from bika.lims.exportimport.load_setup_data import LoadSetupData
        #self.request = makerequest(portal.aq_parent).REQUEST
        #self.request.form['setupexisting'] = 1
        #self.request.form['existing'] = "baobab.lims:test"
        #lsd = LoadSetupData(portal, self.request)
        #lsd()

        logout()

# defining a shared layer/fixture
BAOBAB_SITE_SETUP_FIXTURE = BaobabTestLayer()
BAOBAB_SITE_SETUP_FIXTURE['getBrowser'] = getBrowser

#Remote Library layer
REMOTE_FIXTURE = RemoteLibraryLayer(
    libraries=(AutoLogin, Content, RemoteKeywords,),
    name="RemoteLibrary:RobotRemote"
)

# Site-Setup Layer
SITE_SETUP_LAYER = FunctionalTesting(
    bases=(BAOBAB_SITE_SETUP_FIXTURE,
           REMOTE_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="BaobabTestingLayer:site_setup"
)

# User manual Layer
USER_MANUAL_LAYER = FunctionalTesting(
    bases=(BAOBAB_SITE_SETUP_FIXTURE,
           REMOTE_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="BaobabTestingLayer:user_manual"
)
