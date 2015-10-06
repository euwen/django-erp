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

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from djangoerp.core.utils import clean_http_referer
from djangoerp.core.decorators import obj_permission_required as permission_required
from djangoerp.core.views import SetCancelUrlMixin, ModelListView

from .models import *
from .forms import *

def _get_content_type_by(name):
    model_name = name
    if name[-1] == 's':
        model_name = name[:-1]
    # TODO: a better policy when proxy models with the same name are used.
    return ContentType.objects.filter(model=model_name)[0]

def _get_object_by(object_model, object_id):
    content_type = _get_content_type_by(object_model)
    model_class = content_type.model_class()
    return get_object_or_404(model_class, pk=object_id)  

def _get_object_view_perm(request, *args, **kwargs):
    object_model = kwargs.get('object_model', None)
    content_type = _get_content_type_by(object_model)
    app_label = content_type.app_label
    model_name = content_type.model
    return "%s.view_%s" % (app_label, model_name)

def _get_object(request, *args, **kwargs):
    object_model = kwargs.get('object_model', None)
    object_id = kwargs.get('object_id', None)
    return _get_object_by(object_model, object_id)

def _get_notification(request, *args, **kwargs):
    pk = kwargs.get('pk', None)
    return get_object_or_404(Notification, pk=pk)
    
class NotificationMixin(object):
    model = Notification
    
    def get_queryset(self):
        qs = super(NotificationMixin, self).get_queryset()
        target = _get_object(self.request, *self.args, **self.kwargs)
        return qs.filter(target=target)

@permission_required(_get_object_view_perm, _get_object)
def object_follow(request, object_model, object_id, path=None, **kwargs):
    """The current user starts to follow object's activities.
    """
    obj = _get_object_by(object_model, object_id)
    follower = request.user
    
    if isinstance(obj, Observable):
        obj.add_followers(follower)
        messages.success(request, _("You're now following %(obj)s.") % {"obj": obj}, fail_silently=True)

    return HttpResponseRedirect(path or clean_http_referer(request))

@permission_required(_get_object_view_perm, _get_object)
def object_unfollow(request, object_model, object_id, path=None, **kwargs):
    """The current user stops to follow object's activities.
    """
    obj = _get_object_by(object_model, object_id)
    follower = request.user

    if isinstance(obj, Observable):
        obj.remove_followers(follower)
        messages.success(request, _("You don't follow %(obj)s anymore.") % {"obj": obj}, fail_silently=True)

    return HttpResponseRedirect(path or clean_http_referer(request))
    
class ListNotificationView(NotificationMixin, ModelListView):
    """Displays the list of all filtered notifications.
    """
    field_list = ["title", "created", "read"]
    paginate_by=10
    
    @method_decorator(permission_required(_get_object_view_perm, _get_object))
    @method_decorator(permission_required('notifications.view_notification'))
    def dispatch(self, request, *args, **kwargs):
        return super(ListNotificationView, self).dispatch(request, *args, **kwargs)
    
class DetailNotificationView(NotificationMixin, DetailView):
    """Displays the list of all filtered notifications.
    """
    
    @method_decorator(permission_required(_get_object_view_perm, _get_object))
    def dispatch(self, request, *args, **kwargs):
        return super(DetailNotificationView, self).dispatch(request, *args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        obj = super(DetailNotificationView, self).get_object(*args, **kwargs)
        obj.read = now()
        obj.save()
        return obj
        
class DeleteNotificationView(SuccessMessageMixin, SetCancelUrlMixin, NotificationMixin, DeleteView):
    """Deletes the given notification.
    """
    success_message = _("The notification was deleted successfully.")
    
    @method_decorator(permission_required("notifications.delete_notification", _get_notification))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteNotificationView, self).dispatch(request, *args, **kwargs)
        
    def get_object(self, queryset=None):
        self.object = super(DeleteNotificationView, self).get_object(queryset)
        self.success_url = reverse('notification_list', args=[self.object.target._meta.verbose_name_plural, self.object.target_id])
        return self.object
