# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4:
import doctest
from zope.event import notify
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
from zope.lifecycleevent import ObjectCreatedEvent
from zope.container.contained import ObjectAddedEvent
from zope.container.contained import notifyContainerModified
import plone.multilingual
import plone.multilingual.tests
from plone.multilingual.interfaces import ITranslatable, ILanguage
from OFS.Folder import Folder
from Products.CMFCore.interfaces import IDynamicType
from Products.CMFCore.TypesTool import FactoryTypeInformation


class Demo(Folder):

    implements(ITranslatable, IDynamicType)

    def __init__(self, id):
        self.lang = ''
        self.id = id
        self.portal_type = 'Demo'

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.lang, self.id)


class DemoLanguage(object):

    implements(ILanguage)
    adapts(ITranslatable)

    def __init__(self, context):
        self.context = context

    def get_language(self):
        return self.context.lang

    def set_language(self, lang):
        self.context.lang = lang


class DemoFTI(FactoryTypeInformation):

    def constructInstance(self, container, id, *args, **kw):
        obj = Demo(id)
        container[id] = obj
        notify(ObjectCreatedEvent(obj))
        notify(ObjectAddedEvent(obj, container, id))
        notifyContainerModified(container)
        return obj


class PloneMultilingualLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        xmlconfig.file('configure.zcml', plone.multilingual,
                        context=configurationContext)
        xmlconfig.file('configure.zcml', plone.multilingual.tests,
                        context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.multilingual:default')
        portal._setObject('ob1', Demo('ob1'))
        ILanguage(portal['ob1']).set_language('ca')
        demo_fti = DemoFTI('Demo', content_meta_type="Demo")
        portal.portal_types['Demo'] = demo_fti


PLONEMULTILINGUAL_FIXTURE = PloneMultilingualLayer()
PLONEMULTILINGUAL_INTEGRATION_TESTING = IntegrationTesting(\
    bases=(PLONEMULTILINGUAL_FIXTURE,), name="plone.multilingual:Integration")
PLONEMULTILINGUAL_FUNCTIONAL_TESTING = FunctionalTesting(\
    bases=(PLONEMULTILINGUAL_FIXTURE,), name="plone.multilingual:Functional")
optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
