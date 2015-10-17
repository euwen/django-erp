#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""This file is part of the django ERP project.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2013-2015, django ERP Team'
__version__ = '0.0.5'


from django.test import TestCase
from django.db import models
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string

from . import *
from .models import *
from ..models import Group, User
from ..forms.auth import UserForm
from ..utils import *
from ..utils.models import *
from ..utils.dependencies import *
          

class GetModelTestCase(TestCase):
    def test_invalid_klass(self):
        """Tests "get_model" func must raise a ValueError.
        """
        try:
            m = get_model(None)
            self.fail()
        except ValueError:
            pass
            
    def test_model_klass(self):
        """Tests "get_model" func when a real model class is passed.
        """
        try:
            m = get_model(User)
            self.assertEqual(m, User)
        except ValueError:
            self.fail()
            
    def test_model_instance(self):
        """Tests "get_model" func when a real model instance is passed.
        """
        try:
            u, n = User.objects.get_or_create(username="user_instance")
            m = get_model(u)
            self.assertEqual(m, User)
        except ValueError:
            self.fail()
            
    def test_model_queryset(self):
        """Tests "get_model" func when a real model queryset is passed.
        """
        try:
            qs = User.objects.all()
            m = get_model(qs)
            self.assertEqual(m, User)
        except ValueError:
            self.fail()
            
    def test_model_string(self):
        """Tests "get_model" func when a model string is passed.
        """
        try:
            m = get_model(user_model_string)
            self.assertEqual(m, User)
        except ValueError:
            self.fail()
            
class GetFieldsTestCase(TestCase):
    def setUp(self):
        self.u = User.objects.create(username="u", email="u@u.it", password="password")
        self.f = UserForm(instance=self.u)
        
    def test_get_model_fields(self):
        """Tests retrieving a dict containing all fields of a model instance.
        """
        fields = get_fields(self.u)
        
        self.assertEqual(len(fields), len(self.u._meta.fields) + len(self.u._meta.many_to_many))
        self.assertTrue("username" in fields)
        self.assertTrue(isinstance(fields["username"], models.Field))
        self.assertTrue("email" in fields)
        self.assertTrue(isinstance(fields["email"], models.Field))
        self.assertTrue("password" in fields)
        self.assertTrue(isinstance(fields["password"], models.Field))
        
    def test_get_form_fields(self):
        """Tests retrieving a dict containing all fields of a form instance.
        """
        fields = get_fields(self.f)
        
        self.assertEqual(len(fields), len(self.f._meta.fields))
        self.assertTrue("username" in fields)
        self.assertTrue(isinstance(fields["username"], forms.Field))
        self.assertTrue("email" in fields)
        self.assertTrue(isinstance(fields["email"], forms.Field))
        self.assertFalse("password" in fields)
        self.assertTrue("password1" in fields)
        self.assertTrue(isinstance(fields["password1"], forms.Field))
        self.assertTrue("password2" in fields)
        self.assertTrue(isinstance(fields["password2"], forms.Field))
          
class CleanHTTPRefererTestCase(TestCase):
    def test_no_request(self):
        """Tests when there isn't a request, default_referer must be returned.
        """
        default_referer = '/'
        self.assertEqual(clean_http_referer(None, default_referer), default_referer)
            
    def test_other_site_referer(self):
        """Tests that a valid referer is correctly returned by the function.
        """
        request = FakeRequest()
        self.assertEqual(clean_http_referer(request), "www.test.com")
            
    def test_host_strip_referer(self):
        """Tests the current host should be stripped out.
        """
        expected_referer = '/test'
        request = FakeRequest()
        request.META["HTTP_REFERER"] = request.META['HTTP_HOST'] + expected_referer
        self.assertEqual(clean_http_referer(request), expected_referer)
        
    def test_silently_fail_when_no_http_host(self):
        """Tests that no error should be raised when request hasn't a HTTP_HOST.
        """
        request = FakeRequest()
        del request.META['HTTP_HOST']
        try:
            clean_http_referer(request)
        except:
            self.fail("Failure caused by the absence of HTTP_HOST variable.")
        
class SetPathKwargsTestCase(TestCase):
    def setUp(self):
        self.request = FakeRequest()
        self.request.GET = {
            "next": "/home/",
            "prev": "/home/test/foo/",
            "filter_by": "name",
        }
        
    def test_appending_no_kwargs(self):
        """Tests returning the path as is.
        """
        self.assertEqual(
            set_path_kwargs(FakeRequest()),
            "/home/test/"
        )
        
    def test_appending_get_kargs(self):
        """Tests appending kwargs from request.GET.
        """
        self.assertEqual(
            set_path_kwargs(self.request),
            "/home/test/?filter_by=name;next=/home/;prev=/home/test/foo/"
        )
        
    def test_filtering_existing_kwargs(self):
        """Tests filtering out existing kwargs.
        """
        self.assertEqual(
            set_path_kwargs(self.request, filter_by="id", prev="/"),
            "/home/test/?filter_by=id;next=/home/;prev=/"
        )
        
    def test_removing_invalid_kwargs(self):
        """Tests removing invalid kwargs.
        """
        self.assertEqual(
            set_path_kwargs(self.request, filter_by=None, prev="/"),
            "/home/test/?next=/home/;prev=/"
        )
        
class DependencyTestCase(TestCase):
    def test_satisfied_dependency(self):
        """Tests that when a dependency is satisfied, no error is raised.
        """
        try:
          check_dependency("djangoerp.core")
        except DependencyError:
          self.fail()

    def test_not_satisfied_dependency(self):
        """Tests that when a dependency is not satisfied, an error must be raised.
        """
        try:
          check_dependency("supercalifragidilistichespiralidoso.core")
          self.fail()
        except DependencyError as e:
          self.assertEqual("%s" % e, "A dependency is not satisfied: supercalifragidilistichespiralidoso.core")
   
class RenderingGetFieldTypeTestCase(TestCase):
    def test_get_type_for_field(self):
        """Tests returning a string representing the type of a field.
        """
        self.assertEqual(get_field_type(models.TextField()), "text")
        self.assertEqual(get_field_type(models.IntegerField()), "integer")
        
    def test_get_type_for_choice_field(self):
        """Tests returning a string representation for a field with choices.
        """
        self.assertEqual(get_field_type(models.TextField(choices=[("1", "First")])), "text_choices")
        self.assertEqual(get_field_type(models.IntegerField(choices=[("1", "First")])), "integer_choices")
