import unittest
import json
import logging

from freezegun import freeze_time
from datetime import datetime
from flask_testing import TestCase
from flask import url_for, render_template
from blog import app
from blog.views import CODEVERSION, fetch_everything_from_db, calculate_work_date_stats, find_update_of_site
from google.appengine.ext import testbed
from google.appengine.api import users
from google.appengine.ext import ndb
from blog.forms import PostForm
from blog.models import Tags, Posts, Categories, BlogPost
from blog.utils import find_modified_tags
from blog.search import query_search_index, jsonify_search_results

from . import BlogTestBase

class TestViews(BlogTestBase):
    maxDiff = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        # enable memcache
        self.testbed.init_memcache_stub()

        self.testbed.init_user_stub(enable=True)

        self.testbed.init_search_stub(enable=True)

        self.testbed.setup_env(
            USER_EMAIL='test@example.com',
            USER_ID='123',
            USER_IS_ADMIN='1',
            overwrite=True)

        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

        self.tags = Tags()
        self.categories = Categories()
        self.posts = Posts()

    def test_edit_url_resolves_to_edit_page_view(self):

        passed_days, remaining_days = calculate_work_date_stats()
        form = PostForm()

        response = self.client.get((url_for('tags')))
        if self.posts:
            posts_json = self.posts.to_json()
            site_updated = find_update_of_site(self.posts[len(self.posts) - 1])
        else:
            site_updated = 'NA'
            posts_json = []

        rendered_template = render_template('posts.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=posts_json,
                                            codeversion=CODEVERSION, form=form)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_edit_url_with_contents_is_ok(self):

        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        passed_days, remaining_days = calculate_work_date_stats()
        form = PostForm()

        response = self.client.get((url_for('tags')))
        if self.posts:
            posts_json = self.posts.to_json()
            site_updated = find_update_of_site(self.posts[len(self.posts) - 1])
        else:
            site_updated = 'NA'
            posts_json = []

        rendered_template = render_template('posts.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=posts_json,
                                            codeversion=CODEVERSION, form=form)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_archives_url_resolves_to_archive_page(self):

        passed_days, remaining_days = calculate_work_date_stats()
        form = PostForm()

        response = self.client.get((url_for('archives')))
        if self.posts:
            posts_json = self.posts.to_json()
            site_updated = find_update_of_site(self.posts[len(self.posts) - 1])
        else:
            site_updated = 'NA'
            posts_json = []
        post_tag_names = self.tags.to_json()

        rendered_template = render_template('posts.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=posts_json,
                                            codeversion=CODEVERSION, form=form, posts_tags_names=post_tag_names)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_archives_url_content_is_ok(self):

        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        passed_days, remaining_days = calculate_work_date_stats()
        form = PostForm()

        response = self.client.get((url_for('archives')))
        if self.posts:
            posts_json = self.posts.to_json()
            site_updated = find_update_of_site(self.posts[len(self.posts) - 1])
        else:
            site_updated = 'NA'
            posts_json = []
        post_tag_names = self.tags.to_json()

        rendered_template = render_template('posts.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=posts_json,
                                            codeversion=CODEVERSION, form=form, posts_tags_names=post_tag_names)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_index_page_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('index')))  # create a request object

        rendered_template = render_template("index.html", user_status=users.is_current_user_admin(), siteupdated='NA', \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=self.posts.to_json(),
                                            codeversion=CODEVERSION)
        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_index_page_with_content_is_ok(self):

        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('index')))  # create a request object

        if self.posts:
            posts_json = self.posts.to_json()
            site_updated = find_update_of_site(self.posts[len(self.posts) - 1])
        else:
            site_updated = 'NA'
            posts_json = []

        rendered_template = render_template("index.html", user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated,
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=self.posts.to_json(),
                                            codeversion=CODEVERSION)
        self.assertEqualHTML(rendered_template.decode('utf-8'), response.data.decode('utf-8'))

    def test_selected_post_page_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        current_post = self.posts.get_by_title("a title")

        post_tag_names = current_post.get_tag_names()

        other_posts_tags = self.posts.get_other_tags(current_post.key.id())

        related_posts = []

        response = self.client.get(url_for('view_a_post', category="category", year=current_post.timestamp.year,
                                           month=current_post.timestamp.month, title="a title"))
        for post in self.posts:
            if post.key != current_post.key:
                for tag in post.tags:
                    if tag in other_posts_tags:
                        related_posts.append(post)

        category = post.category.get().category

        rendered_template = render_template('singlepost.html', user_status=users.is_current_user_admin(),
                                            siteupdated='NA', \
                                            daysleft=remaining_days, dayspassed=passed_days, RelatedPosts=related_posts, \
                                            Post=current_post, posttagnames=post_tag_names, category=category)

        self.assertEqual(rendered_template.encode("utf-8"), response.data)

    def test_tag_pag_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('index')))  # create a request object

        rendered_template = render_template("index.html", user_status=users.is_current_user_admin(), siteupdated='NA', \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=self.posts.to_json(),
                                            codeversion=CODEVERSION)
        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_delete_post(self):

        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        response = self.client.delete(url_for('delete_post', id=post_key.id()))

        self.assertEqual("OK", response.json["msg"])

    def test_get_post(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]

        existing_tag_keys = self.tags.add(existing_tags)

        post_key = self.posts.add("a title", "body text", category_key, existing_tag_keys, "this is a summary")

        asked_post = post_key.get()

        post_tag_names = asked_post.get_tag_names()

        tag_names = self.tags.get_names()

        data = {u"title": asked_post.title, u"body": asked_post.body, u"category":
            asked_post.category.get().category,
                 u"catid": str(category_key.id()).decode('utf8'), u"id": str(asked_post.key.id()).decode('utf8'), \
                 u"tags": post_tag_names,
                 u"date": asked_post.timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8')
                    , u"updated":
                     asked_post.updated.strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8'),
                 }

        response = self.client.get(url_for("get_post", id=post_key.id()))

        self.assertDictEqual(data, response.json)

    def test_add_post(self):

        existing_tags = [u"a new new tag", u"a new tag"]
        freezer = freeze_time("2017-03-20 17:48:18")
        freezer.start()
        json_data = {u'category': u'category', u'tags': existing_tags, u"summary": u"this is a summary",
                     u'title': u'a title',u'body': u'body text', u'timestamp': datetime.now().
                strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8'),
                     u'updated': datetime.now().
                strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8')}

        response = self.client.post(url_for('main'), content_type='application/json',
                                   data=json.dumps(json_data))
        json_data[u"id"] = 4
        self.assertDictEqual(json_data, response.json)
        freezer.stop()

    def test_no_post(self):

        json_data = {}

        response = self.client.get(url_for('main'))

        self.assertDictEqual(json_data, response.json)

    def test_edit_post(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]
        editing_tags = ["a new tag", "tag to added"]  # final tags are "a new tag", "tag to added"

        existing_tag_keys = self.tags.add(existing_tags)

        post_key = self.posts.add("a title", "body text", category_key, existing_tag_keys, "this is a summary")

        self.posts.add("a title 2", "body text 2", category_key, existing_tag_keys, "this is a summary 2")

        updating_post = post_key.get()

        json_data = {'category': 'category', 'tags': editing_tags, 'title': 'a title', 'body': 'body text'}

        response = self.client.put(url_for('edit_post', id=post_key.id()), content_type='application/json',
                                   data=json.dumps(json_data))

        tag_names = [u"a new tag", u"a new new tag", u"tag to added"]
        post_tag_names = [u"a new tag", u"tag to added"]

        data = {u"title": updating_post.title, u"body": updating_post.body, u"category":
            updating_post.category.get().category,
                 u"catid": str(category_key.id()).decode('utf8'), u"id": str(updating_post.key.id()).decode('utf8'), \
                 u"tags": post_tag_names,
                 u"date": updating_post.timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8')
                    , u"updated":
                     updating_post.updated.strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8'),
                 }

        self.assertDictEqual(data, response.json)

    def test_about_page(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]

        existing_tag_keys = self.tags.add(existing_tags)

        self.posts.add("about", "body text", category_key, existing_tag_keys, "this is a summary")

        requested_post = self.posts.get_by_title('about')

        response = self.client.get(url_for('aboutpage'))

        passed_days, remaining_days = calculate_work_date_stats()

        if self.posts:
            posts_json = self.posts.to_json()
            site_updated = find_update_of_site(self.posts[len(self.posts) - 1])
        else:
            site_updated = 'NA'

        rendered_template = render_template('about.html',user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,Post=requested_post,
                           codeversion=CODEVERSION)

        self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    def test_search_results(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]

        existing_tag_keys = self.tags.add(existing_tags)

        self.posts.add("about", "body text", category_key, existing_tag_keys, "this is a summary")

        passed_days, remaining_days = calculate_work_date_stats()

        site_updated = find_update_of_site(self.posts[len(self.posts) - 1])

        rendered_template = render_template("index.html",  user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days,
                                            tags=self.tags, categories=self.categories,
                                            posts=self.posts.to_json(),
                                            codeversion=CODEVERSION)

        response = self.client.get(url_for('searchresults', q="body"))

        self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    def test_search_query(self):

        category_key = self.categories.add("category")
        existing_tags = ["a new tag", "a new new tag"]
        existing_tag_keys = self.tags.add(existing_tags)

        self.posts.add("about", "body text", category_key, existing_tag_keys, "this is a summary")

        query_string = "body"
        results = query_search_index(query_string)
        data = jsonify_search_results(results)

        response = self.client.get(url_for('search', q="body"), content_type='application/json',
                                   data=json.dumps(json_data))
        print (response)

        return self.assertDictEqual({"data":data}, response.data)