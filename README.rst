plone.multilingual
==================

This package contains the core functionality for the next generation multilingual engine.

These are the main artifacts and its purposes:

    canonical:
        * the canonical organizes the information about a "translation-group"
        * it's using a dictionary with language-codes as keys and uuids 
        (provided by plone.uuid) as values

    storage:
        * persistent storage, which holds the canonicals in an IOBTree
        * the OOBTree's key is the UUID of the content, the according value is the canonical

    manager:
        * adapter for ITranslatable
        * provides the translations API

    adapters:
        * ITranslationLocator - where to put a translation
        * ITranslationIdChooser - generates a valid id for a translation
        * ITranslationCloner - copy the language-independent content to the translation
        * ITranslationFactory - creates the translation

In order to have a test we have a type called Demo that has an adapter
called DemoLanguage that will allow to get the language of the object::

    >>> from plone.multilingual.interfaces import ITranslationManager
    >>> from plone.multilingual.interfaces import ILanguage
    >>> from plone.app.testing import setRoles, login, TEST_USER_ID, TEST_USER_NAME

    >>> portal = layer['portal']
    >>> setRoles(portal, TEST_USER_ID, ['Manager'])
    >>> login(portal, TEST_USER_NAME)
    >>> portal.invokeFactory('Folder', 'ob1', title=u"An archetypes based folder")
    'ob1'

    >>> ILanguage(portal['ob1']).set_language('ca')

Ensuring that the new object gets its UUID::
    
    >>> from plone.uuid.interfaces import IUUID
    >>> ob1_uuid = IUUID(portal['ob1'])
    >>> isinstance(ob1_uuid, str)
    True

We create a new translation in 'en' language::

   >>> ITranslationManager(portal['ob1']).add_translation('en')

We try to create a new translation in 'ca' that already exists::

    >>> ITranslationManager(portal['ob1']).add_translation('ca')
    Traceback (most recent call last):
    ...
    KeyError: 'Translation already exists'

We try to create a new translation without language::

    >>> ITranslationManager(portal['ob1']).add_translation(None)
    Traceback (most recent call last):
    ...
    KeyError: 'There is no target language'

We get the 'en' translation::

    >>> ITranslationManager(portal['ob1']).get_translation('en')
    <ATFolder at /plone/ob1-en>
    >>> ILanguage(ITranslationManager(portal['ob1']).get_translation('en')).get_language() == 'en'
    True

let's get all the translations::

    >>> ITranslationManager(portal['ob1']).get_translations()
    {'ca': <ATFolder at /plone/ob1>, 'en': <ATFolder at /plone/ob1-en>}

let's get only the languages::

    >>> ITranslationManager(portal['ob1']).get_translated_languages()
    ['ca', 'en']

has_translation::

    >>> ITranslationManager(portal['ob1']).has_translation('en')
    True

    >>> ITranslationManager(portal['ob1']).has_translation('it')
    False

register_translation with invalid language::

    >>> ITranslationManager(portal['ob1']).remove_translation('en')
    >>> ITranslationManager(portal['ob1']).register_translation('', portal['ob1-en'])
    Traceback (most recent call last):
    ...
    KeyError: 'There is no target language'

register a translation with content::

    >>> ITranslationManager(portal['ob1']).register_translation('en', portal['ob1-en'])
    >>> ITranslationManager(portal['ob1']).get_translations()
    {'ca': <ATFolder at /plone/ob1>, 'en': <ATFolder at /plone/ob1-en>}

changing the content-language (there should act a subscriber)::

    >>> ILanguage(portal['ob1-en']).set_language('it')
    >>> from zope.event import notify
    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> notify(ObjectModifiedEvent(portal['ob1-en']))
    >>> ITranslationManager(portal['ob1']).get_translations()
    {'ca': <ATFolder at /plone/ob1>, 'it': <ATFolder at /plone/ob1-en>}

test the delete-subscriber::

    >>> from OFS.event import ObjectWillBeRemovedEvent
    >>> notify(ObjectWillBeRemovedEvent(ITranslationManager(portal['ob1']).get_translation('it')))
    >>> ITranslationManager(portal['ob1']).get_translations()
    {'ca': <ATFolder at /plone/ob1>}

Default-Adapters
----------------
id-chooser::

    >>> from plone.multilingual.interfaces import ITranslationIdChooser
    >>> chooser = ITranslationIdChooser(portal['ob1-en'])
    >>> chooser(portal, 'es')
    'ob1-es'

locator::

    >>> ITranslationManager(portal['ob1']).add_translation('es')
    >>> child_id = portal.ob1.invokeFactory('Folder', 'ob1_child', language="ca")

    >>> from plone.multilingual.interfaces import ITranslationLocator
    >>> locator = ITranslationLocator(portal['ob1-en'])
    >>> locator('es') == portal
    True

    >>> child_locator = ITranslationLocator(portal.ob1.ob1_child)
    >>> child_locator('es') == portal['ob1-es']
    True

    >>> ITranslationManager(portal['ob1']).remove_translation('es')

Convert intids to uuids upgrade step
------------------------------------

An upgrade step is available in case of having an existing site with the experimental
0.1 plone.multilingual version::

    >>> from plone.multilingual.upgrades.to02 import upgrade

.. note::
    You must reinstall the plone.multilingual package in order to install the required new
    utility in place before upgrading. If you are using a version of Dexterity below 2.0, you 
    must install the package plone.app.referenceablebehavior and enable the *Referenceable* 
    (plone.app.referenceablebehavior.referenceable.IReferenceable) behavior for all your 
    Dexterity content types before you attempt to upgrade your site.

You can run the @@pml-upgrade view at the root of your site or follow the upgrade step in
portal_setup > upgrades. If you can't see the upgrade step, press *Show old upgrades* and 
select the *Convert translation based initids to uuids (0.1 → 02)*

uninstall-profile
-----------------
::

    >>> from plone.app.testing import applyProfile
    >>> applyProfile(portal, 'plone.multilingual:uninstall')

we shouldn't find the storage-utility anymore::

    >>> from plone.multilingual.interfaces import IMultilingualStorage
    >>> gsm = portal.getSiteManager()
    >>> gsm.queryUtility(IMultilingualStorage) == None
    True
