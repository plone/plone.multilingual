# -*- coding: utf-8 -*-
import doctest
from plone.app.testing import (
    PLONE_FIXTURE,
    PloneSandboxLayer,
    applyProfile,
    IntegrationTesting,
    FunctionalTesting,
)
from zope.configuration import xmlconfig
from zope.interface import implements
from zope.component import adapts
from plone.multilingual.interfaces import ITranslatable, ILanguage


class DemoLanguage(object):

    implements(ILanguage)
    adapts(ITranslatable)

    def __init__(self, context):
        self.context = context

    def get_language(self):
        return self.context.getLanguage()

    def set_language(self, lang):
        self.context.setLanguage(lang)


class PloneMultilingualLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.uuid
        import plone.multilingual

        # load ZCML
        xmlconfig.file('configure.zcml', plone.multilingual,
                        context=configurationContext)
        xmlconfig.file('configure.zcml', plone.multilingual.tests,
                        context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.multilingual:default')
        from zope.interface import classImplements
        from Products.ATContentTypes.content.folder import ATFolder
        classImplements(ATFolder, ITranslatable)


PLONEMULTILINGUAL_FIXTURE = PloneMultilingualLayer()
PLONEMULTILINGUAL_INTEGRATION_TESTING = IntegrationTesting(\
    bases=(PLONEMULTILINGUAL_FIXTURE,), name="plone.multilingual:Integration")
PLONEMULTILINGUAL_FUNCTIONAL_TESTING = FunctionalTesting(\
    bases=(PLONEMULTILINGUAL_FIXTURE,), name="plone.multilingual:Functional")
optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
