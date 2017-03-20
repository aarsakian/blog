from datetime import datetime

from freezegun import freeze_time

from google.appengine.ext import testbed

from google.appengine.ext import ndb

from google.appengine.api.search import Document
from google.appengine.api import search

from blog.search import create_document,  add_document_in_search_index,\
    delete_document, _INDEX_NAME, query_search_index, jsonify_search_results

from . import BlogTestBase

class TestModels(BlogTestBase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.

        self.testbed.init_search_stub(enable=True)
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

        self.document_id = u'54357456'
        self.index = search.Index(name=_INDEX_NAME)

    def test_create_document(self):

        document = create_document(self.document_id, "a title", "body", "a summary", "a category", datetime.now())
        self.assertIsInstance(document, Document)
        self.assertEqual(self.document_id, document.doc_id)

    def test_add_document_in_search_index(self):
        add_document_in_search_index(self.document_id, "a title", "body", "a summary", "a category", datetime.now())
        results = self.index.search("title")
        scored_document = results.results[0]
        self.assertEqual(self.document_id, scored_document.doc_id)

    def test_delete_document(self):
        add_document_in_search_index(self.document_id, "a title", "body", "a summary", "a category", datetime.now())
        delete_document(self.document_id)
        results = self.index.search("title")
        self.assertItemsEqual([], results)

    def test_query_search_index(self):
        query_string = "title"
        add_document_in_search_index(self.document_id, "a title", "body", "a summary", "a category", datetime.now())

        results = query_search_index(query_string)
        scored_document = results.results[0]

        self.assertEqual(self.document_id, scored_document.doc_id)

        query_string_not_existing = "title2"
        results = query_search_index(query_string_not_existing)

        self.assertItemsEqual([], results)

    def test_jsonify_search_results(self):
        freezer = freeze_time("2017-03-20 17:48:18")
        freezer.start()
        add_document_in_search_index(self.document_id, "a title", "body test", "a summary", "a category", datetime.now())

        query_string = "body"

        results = query_search_index(query_string)

        jsonified_results = jsonify_search_results(results)

        correct_jsonified_results = {'id': self.document_id, u'title': u'a title', u'body': u'body',u'summary':
                                     u'a summary', u'category': u'a category', u'timestamp': datetime.now()}

        self.assertDictEqual(correct_jsonified_results, jsonified_results[0])
        freezer.stop()
