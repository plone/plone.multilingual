from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityContent
from plone.uuid.handlers import addAttributeUUID
from plone.uuid.interfaces import IUUID
from zope.component import getUtility, queryUtility
from zope.component import getAllUtilitiesRegisteredFor
from plone.multilingual.interfaces import IMultilingualStorage
from zope.intid.interfaces import IIntIds
from plone.multilingual.canonical import Canonical

from Products.Five.browser import BrowserView
import logging


def upgrade(context):
    # Add missing UIDs to already existing dexterity content types
    # Borrowed from plone.app.dexterity :)

    logger = logging.getLogger('plone.multilingual')
    logger.info('Adding missing UUIDs to the already existing '
                'dexterity content types')

    catalog = getToolByName(context, 'portal_catalog')
    query = {'object_provides': IDexterityContent.__identifier__}
    results = catalog.unrestrictedSearchResults(query)
    for b in results:
        ob = b.getObject()
        if IUUID(ob, None) is None:
            addAttributeUUID(ob, None)
            ob.reindexObject(idxs=['UID'])
    logger.info('Added %s missing UUIDs' % len(results))

    # Upgrade utility, and convert intids to uuids
    intids = queryUtility(IIntIds)
    if not intids:
        intids = getAllUtilitiesRegisteredFor(IIntIds)[0]

    oldstorage = getToolByName(context, 'canonical_storage')

    for canonicalintid in oldstorage.canonicals:
        canonicaluuid = IUUID(intids.getObject(canonicalintid))
        translations = oldstorage.canonicals[canonicalintid].languages
        upgradedcanonical = Canonical()
        for lang in translations.keys():
            langintid = translations[lang]
            langobj = intids.getObject(langintid)
            languuid = IUUID(langobj)
            upgradedcanonical.add_item(lang, languuid)
        storage = getUtility(IMultilingualStorage)
        storage.add_canonical(canonicaluuid, upgradedcanonical)
        logger.info('%s' % upgradedcanonical.languages)


class upgradeView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        upgrade(self.context)
        return 'plone.multilingual utility upgraded successfully'
