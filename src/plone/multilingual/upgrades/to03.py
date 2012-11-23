from zope.component import getUtility
from plone.multilingual.interfaces import IMultilingualStorage
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import queryUtility
from plone.multilingual.interfaces import IMutableTG
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
import transaction


def upgrade(context):
    # Move the Storage to catalog
    storage = getUtility(IMultilingualStorage)
    canonicals = storage.get_canonicals()
    already_added_canonicals = []
    generator = queryUtility(IUUIDGenerator)
    for canonical in canonicals.keys():
        canonical_object = canonicals[canonical]
        canonical_languages = canonical_object.get_keys()
        if id(canonical_object) not in already_added_canonicals:
            tg = generator()
            for canonical_language in canonical_languages:
                obj = uuidToObject(canonical_object.get_item(canonical_language))
                if obj is not None:
                    IMutableTG(obj).set(tg)
                    obj.reindexObject()
            already_added_canonicals.append(id(canonical_object))
    # Uninstall the utility
    getSite().getSiteManager().unregisterUtility(storage, IMultilingualStorage)
    del storage
    # Install the index and rebuild
    pcatalog = getToolByName(context, 'portal_catalog', None)
    if pcatalog is not None:
        indexes = pcatalog.indexes()
        if 'TranslationGroup' not in indexes:
            pcatalog.addIndex('TranslationGroup', 'FieldIndex')
            pcatalog.manage_reindexIndex(ids=['TranslationGroup'])
        else:
            pcatalog.clearFindAndRebuild()
    transaction.commit()
