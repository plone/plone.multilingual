# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4:
from zope import interface
from BTrees.IOBTree import IOBTree
from OFS.SimpleItem import SimpleItem
from plone.multilingual.interfaces import ICanonicalStorage


class CanonicalStorage(SimpleItem):

    interface.implements(ICanonicalStorage)
    id = 'canonical_storage'

    def __init__(self):
        self.id = id
        self.canonicals = IOBTree()

    def get_canonical(self, id):
        """ get a canonical for a specific content-id """
        canonical = None
        if id in self.canonicals:
            canonical = self.canonicals[id]
        return canonical

    def add_canonical(self, id, canonical):
        """ add a canonical """
        self.canonicals.insert(id, canonical)

    def remove_canonical(self, id):
        """ remove a canonical """
        self.canonicals.pop(id)
