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
from django.contrib.auth import get_user_model

from . import *
from ..signals import *
        

class SignalTestCase(TestCase):
    def test_manage_author_permissions(self):
        """Tests that "manage_author_permissions" auto-generate perms for author. 
        """
        user_model = get_user_model()
        
        u3, n = user_model.objects.get_or_create(username="u3", password="pwd")
        u4, n = user_model.objects.get_or_create(username="u4")
        
        clear_perm_caches(u3)
        clear_perm_caches(u4)
        
        self.assertFalse(ob.has_perm(u3, "%s.view_user" % auth_app, u4))
        self.assertFalse(ob.has_perm(u3, "%s.change_user" % auth_app, u4))
        self.assertFalse(ob.has_perm(u3, "%s.delete_user" % auth_app, u4))
        
        self.assertFalse(ob.has_perm(u4, "%s.view_user" % auth_app, u3))
        self.assertFalse(ob.has_perm(u4, "%s.change_user" % auth_app, u3))
        self.assertFalse(ob.has_perm(u4, "%s.delete_user" % auth_app, u3))
        
        manage_author_permissions(user_model)
        prev_user = logged_cache.user
        
        # The current author ("logged" user) is now u3.
        logged_cache.user = u3
        u5, n = user_model.objects.get_or_create(username="u5")
        u6, n = user_model.objects.get_or_create(username="u6")
        
        clear_perm_caches(u3)
        clear_perm_caches(u4)
        clear_perm_caches(u5)
        clear_perm_caches(u6)
        
        self.assertTrue(ob.has_perm(u3, "%s.view_user" % auth_app, u5))
        self.assertTrue(ob.has_perm(u3, "%s.change_user" % auth_app, u5))
        self.assertTrue(ob.has_perm(u3, "%s.delete_user" % auth_app, u5))
        
        self.assertFalse(ob.has_perm(u5, "%s.view_user" % auth_app, u3))
        self.assertFalse(ob.has_perm(u5, "%s.change_user" % auth_app, u3))
        self.assertFalse(ob.has_perm(u5, "%s.delete_user" % auth_app, u3))
        
        # Restores previous cached user.
        logged_cache.user = prev_user
        
        manage_author_permissions(user_model, False)
        
    def test_author_is_only_the_very_first_one(self):
        """Tests that perms must be auto-generated only for the first author. 
        """
        user_model = get_user_model()
        
        u3, n = user_model.objects.get_or_create(username="u3")
        u4, n = user_model.objects.get_or_create(username="u4")
        
        manage_author_permissions(get_user_model())
        prev_user = logged_cache.user
        
        # The current author ("logged" user) is now u3.
        logged_cache.user = u3
        u7, n = user_model.objects.get_or_create(username="u7")
        
        clear_perm_caches(u3)
        clear_perm_caches(u4)
        
        self.assertTrue(ob.has_perm(u3, "%s.view_user" % auth_app, u7))
        self.assertTrue(ob.has_perm(u3, "%s.change_user" % auth_app, u7))
        self.assertTrue(ob.has_perm(u3, "%s.delete_user" % auth_app, u7))
        
        self.assertFalse(ob.has_perm(u4, "%s.view_user" % auth_app, u7))
        self.assertFalse(ob.has_perm(u4, "%s.change_user" % auth_app, u7))
        self.assertFalse(ob.has_perm(u4, "%s.delete_user" % auth_app, u7))
        
        # The current author ("logged" user) is now u4.
        logged_cache.user = u4
        
        u7.username = "u7_edited"
        u7.save()
        
        clear_perm_caches(u4)
        
        self.assertFalse(ob.has_perm(u4, "%s.view_user" % auth_app, u7))
        self.assertFalse(ob.has_perm(u4, "%s.change_user" % auth_app, u7))
        self.assertFalse(ob.has_perm(u4, "%s.delete_user" % auth_app, u7))
        
        # Restores previous cached user.
        logged_cache.user = prev_user
        
        manage_author_permissions(user_model, False)
        
    def test_author_only_if_authenticated(self):
        """Tests that perms are auto-generated only if author isn't anonymous. 
        """
        prev_user = logged_cache.user
        
        # The current author is now anonyous.
        logged_cache.clear()
        
        u8, n = get_user_model().objects.get_or_create(username="u8")
        
        clear_perm_caches(u8)
        
        self.assertFalse(logged_cache.has_user)
        self.assertFalse(ob.has_perm(logged_cache.user, "%s.view_user" % auth_app, u8))
        self.assertFalse(ob.has_perm(logged_cache.user, "%s.change_user" % auth_app, u8))
        self.assertFalse(ob.has_perm(logged_cache.user, "%s.delete_user" % auth_app, u8))
        
        # Restores previous cached user.
        logged_cache.user = prev_user
