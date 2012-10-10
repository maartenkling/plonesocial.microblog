import random
import string
import time

from zope.component import queryUtility
from zope.app.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from persistent import Persistent
import transaction
from Products.Five import BrowserView

from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.microblog.statusupdate import StatusUpdate

# funkload only
from plonesocial.microblog.unrestricted import execute_under_special_role

ANNOTATION_KEY = 'plonesocial.microblog:funkload'


def addStatus():
    execute_under_special_role(getSite(), "Manager", _addStatus)


def _addStatus():
    text = ''.join(random.sample(string.printable,
                                 random.randint(8, 20)))
    # pick between zero and two tags:
    possible_tags = ['#random', '#fuzzy', '#beer']
    tags = random.sample(possible_tags, random.randint(0, 2))
    text = text + ' ' + ' '.join(tags)
    status = StatusUpdate(text)
    container = queryUtility(IMicroblogTool)
    container.add(status)


class FunkloadView(BrowserView):
    """A special load testing helper view.

    Should *not* be available in any production site
    since it allows Anonymous users to insert
    dummy microblog status updates.
    """

    def __call__(self):
        t0 = time.time()
        if 'noop' in self.request.form.keys():
            return 'NOOP. %s' % (time.time() - t0)

        elif 'dummy' in self.request.form.keys():
            return self.insert_dummy()
        elif 'dummy100' in self.request.form.keys():
            return self.insert_dummy100()

        if 'batch' in self.request.form.keys():
            batch = int(self.request.form['batch'])
        else:
            batch = 1
        for i in xrange(batch):
            addStatus()
        return '%s batched. %s' % (batch, (time.time() - t0))

    def insert_dummy(self):
        annotations = IAnnotations(getSite())
        if not ANNOTATION_KEY in annotations:
            annotations[ANNOTATION_KEY] = Dummy()
        dummy = annotations[ANNOTATION_KEY]
        dummy.foo = random.random()
        transaction.commit()
        return dummy.foo

    def insert_dummy100(self):
        annotations = IAnnotations(getSite())
        if not ANNOTATION_KEY in annotations:
            annotations[ANNOTATION_KEY] = Dummy()
        dummy = annotations[ANNOTATION_KEY]
        try:
            check = dummy.children  # pyflakes.ignore
        except AttributeError:
            dummy.children = []
        for i in xrange(100):
            dummy.children.append(Dummy())
        dummy._p_changed = True
        transaction.commit()
        return 'Inserted 100 dummy objects. Total: %s.' % len(dummy.children)


class Dummy(Persistent):

    def __init__(self, foo='bar'):
        self.foo = foo
