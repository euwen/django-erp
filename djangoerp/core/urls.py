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


from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.views import (login, logout_then_login)
from .views import *


urlpatterns = [

    # User authentication management.
    url(r'^users/login/$', login, {'template_name': 'auth/login.html'}, name='user_login'),
    url(r'^users/logout/confirm/$', TemplateView.as_view(template_name="auth/confirm_logout.html"), name='user_confirm_logout'),
    url(r'^users/logout/$', view=logout_then_login, name='user_logout'),
    url(r'^users/(?P<pk>\d+)/$', view=DetailUserView.as_view(), name='user_detail'),
    url(r'^users/(?P<pk>\d+)/edit/$', view=UpdateUserView.as_view(), name='user_edit'),
    url(r'^users/(?P<pk>\d+)/delete/$', view=DeleteUserView.as_view(), name='user_delete'),
    
    # About.
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name='about'),
    
    # Homepage.
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='home'),
]
