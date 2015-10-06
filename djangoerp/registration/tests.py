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
from django.conf import settings

from .models import *

if "djangoerp.registration" in settings.INSTALLED_APPS:

    class AppConfigTestCase(TestCase):
        def test_initial_fixture_installation(self):
            """Tests installation of initial fixture.
            """
            from djangoerp.menus.models import Link, Menu

            user_area_not_logged_menu, is_new = Menu.objects.get_or_create(
                slug="user_area_not_logged"
            )
            
            # Links.
            register_link, is_new = Link.objects.get_or_create(
                slug="register",
                menu_id=user_area_not_logged_menu.pk
            )
            self.assertTrue(register_link)
            self.assertFalse(is_new)
