import unittest2 as unittest
from Products.CMFCore.utils import getToolByName

from plone.testing.z2 import Browser

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles

from plone.multilingual.interfaces import ILanguage
from plone.multilingual.testing import PLONEMULTILINGUAL_INTEGRATION_TESTING
from plone.multilingual.utils import multilingualMoveObject
from plone.app.multilingual.tests.utils import makeContent, makeTranslation

import transaction


class PMUtils(unittest.TestCase):

    layer = PLONEMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('ca')
        language_tool.addSupportedLanguage('es')

    def test_move_content_proper_language_folder(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'new1', title=u"An archetypes based doc")
        new1 = self.portal['new1']
        transaction.commit()
        multilingualMoveObject(new1, 'ca')
