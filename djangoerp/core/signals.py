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

from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .utils import get_model
from .cache import LoggedInUserCache
from .models import Permission, ObjectPermission, Group

## HANDLERS ##

def _update_author_permissions(sender, instance, raw, created, **kwargs):
    """Updates the permissions assigned to the author of the given object.
    """
    author = LoggedInUserCache().user
    if author and author.is_authenticated():
        content_type = ContentType.objects.get_for_model(sender)
        app_label = content_type.app_label
        model_name = content_type.model

        if created:        
            can_view_this_object, is_new = ObjectPermission.objects.get_or_create_by_natural_key("view_%s" % model_name, app_label, model_name, instance.pk)
            can_change_this_object, is_new = ObjectPermission.objects.get_or_create_by_natural_key("change_%s" % model_name, app_label, model_name, instance.pk)
            can_delete_this_object, is_new = ObjectPermission.objects.get_or_create_by_natural_key("delete_%s" % model_name, app_label, model_name, instance.pk)

            can_view_this_object.users.add(author)
            can_change_this_object.users.add(author)
            can_delete_this_object.users.add(author)
        
def manage_author_permissions(cls, enabled=True):
    """Adds permissions assigned to the author of the given object.
    
    Connects the post_save signal of the given model class to the handler which
    adds default permissions to the current user. i.e.:
    
    >> manage_author_permissions(Project)
    
    It will add default view, change and delete permissions for each Project's
    instances created by the current user.
    
    To disconnect:
    
    >> manage_author_permissions(Project, False)
    """
    cls = get_model(cls)
    dispatch_uid = "update_%s_permissions" % cls.__name__.lower()
    
    if enabled:
        post_save.connect(_update_author_permissions, cls, dispatch_uid=dispatch_uid)
        
    else:
        post_save.disconnect(_update_author_permissions, cls, dispatch_uid=dispatch_uid)

def user_post_save(sender, instance, created, *args, **kwargs):
    """Add view/delete/change object permissions to users (on themselves).
    
    It also adds new user instances to "users" group.
    """
    auth_app, sep, user_model_name = settings.AUTH_USER_MODEL.rpartition('.')
    user_model_name = user_model_name.lower()
    
    # All new users have full control over themselves.
    can_view_this_user, is_new = ObjectPermission.objects.get_or_create_by_natural_key("view_%s" % user_model_name, auth_app, user_model_name, instance.pk)
    can_change_this_user, is_new = ObjectPermission.objects.get_or_create_by_natural_key("change_%s" % user_model_name, auth_app, user_model_name, instance.pk)
    can_delete_this_user, is_new = ObjectPermission.objects.get_or_create_by_natural_key("delete_%s" % user_model_name, auth_app, user_model_name, instance.pk)
    can_view_this_user.users.add(instance)
    can_change_this_user.users.add(instance)
    can_delete_this_user.users.add(instance)
    
    # All new users are members of "users" group.
    if created:
        users_group, is_new = Group.objects.get_or_create(name='users')
        instance.groups.add(users_group)

def add_view_permission(sender, instance, **kwargs):
    """Adds a view permission related to each new ContentType instance.
    """
    if isinstance(instance, ContentType):
        codename = "view_%s" % instance.model
        Permission.objects.get_or_create(content_type=instance, codename=codename, name="Can view %s" % instance.name)    

## CONNECTIONS ##

post_save.connect(user_post_save, get_user_model())
post_save.connect(add_view_permission, ContentType)
