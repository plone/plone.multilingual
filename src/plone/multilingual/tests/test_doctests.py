import unittest2 as unittest
import doctest
from plone.testing import layered
from plone.multilingual.testing import (
    PLONEMULTILINGUAL_INTEGRATION_TESTING,
    PLONEMULTILINGUAL_FUNCTIONAL_TESTING,
    optionflags,
)

integration_tests = [
    'README.rst',
]
functional_tests = [
]


def test_suite():
    return unittest.TestSuite(
        [layered(doctest.DocFileSuite('%s' % f, package='plone.multilingual',
                                      optionflags=optionflags),
                 layer=PLONEMULTILINGUAL_INTEGRATION_TESTING)
            for f in integration_tests]
        +
        [layered(doctest.DocFileSuite('%s' % f, package='plone.multilingual',
                                      optionflags=optionflags),
                 layer=PLONEMULTILINGUAL_FUNCTIONAL_TESTING)
            for f in functional_tests]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
