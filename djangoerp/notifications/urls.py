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

from .views import *


urlpatterns = [

    url(r'^(?P<object_model>[\w\d\_]+)/(?P<object_id>\d+)/notifications/follow/$', view=object_follow, name='object_follow'),
    url(r'^(?P<object_model>[\w\d\_]+)/(?P<object_id>\d+)/notifications/unfollow/$', view=object_unfollow, name='object_unfollow'),
    url(r'^(?P<object_model>[\w\d\_]+)/(?P<object_id>\d+)/notifications/$', view=ListNotificationView.as_view(), name='notification_list'),
    url(r'^(?P<object_model>[\w\d\_]+)/(?P<object_id>\d+)/notifications/(?P<pk>\d+)/$', view=DetailNotificationView.as_view(), name='notification_detail'),
    url(r'^(?P<object_model>[\w\d\_]+)/(?P<object_id>\d+)/notifications/(?P<pk>\d+)/delete/$', view=DeleteNotificationView.as_view(), name='notification_delete'),
]
