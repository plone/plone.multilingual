# -*- coding: utf-8 -*-
from OFS.Folder import Folder
from Testing import ZopeTestCase as ztc

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.multilingual.interfaces import ITranslatable, ILanguage
from zope.configuration import xmlconfig
from zope.interface import implements
from zope.component import adapts

import doctest
import transaction


class DemoLanguage(object):

    implements(ILanguage)
    adapts(ITranslatable)

    def __init__(self, context):
        self.context = context

    def get_language(self):
        return self.context.Language()

    def set_language(self, lang):
        self.context.setLanguage(lang)


class PloneMultilingualLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def setUpZope(self, app, configurationContext):
        import plone.uuid
        import plone.multilingual

        # load ZCML
        xmlconfig.file('testing.zcml', plone.multilingual,
                        context=configurationContext)
        xmlconfig.file('configure.zcml', plone.multilingual.tests,
                       context=configurationContext)

        # Support sessionstorage in tests
        app.REQUEST['SESSION'] = self.Session()
        if not hasattr(app, 'temp_folder'):
            tf = Folder('temp_folder')
            app._setObject('temp_folder', tf)
            transaction.commit()

        ztc.utils.setupCoreSessions(app)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.multilingual:testing')
        from zope.interface import classImplements
        from Products.ATContentTypes.content.folder import ATFolder
        classImplements(ATFolder, ITranslatable)


PLONEMULTILINGUAL_FIXTURE = PloneMultilingualLayer()

PLONEMULTILINGUAL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEMULTILINGUAL_FIXTURE, ),
    name="plone.multilingual:Integration")

PLONEMULTILINGUAL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEMULTILINGUAL_FIXTURE, ),
    name="plone.multilingual:Functional")

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
