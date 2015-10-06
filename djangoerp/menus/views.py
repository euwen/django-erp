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

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from djangoerp.core.utils import clean_http_referer
from djangoerp.core.views import SetCancelUrlMixin, ModelListView
from djangoerp.core.decorators import obj_permission_required as permission_required

from .utils import get_bookmarks_for
from .models import *
from .forms import *

def _get_bookmarks(request, *args, **kwargs):
    return get_bookmarks_for(request.user.username)

def _get_bookmark(request, *args, **kwargs):
    bookmarks = _get_bookmarks(request, *args, **kwargs)
    return get_object_or_404(Bookmark, slug=kwargs.get('slug', None), menu=bookmarks)
    
class BookmarkMixin(object):
    model = Bookmark
    
    def get_queryset(self):
        qs = super(BookmarkMixin, self).get_queryset()
        return qs.filter(menu=_get_bookmarks(self.request, self.args, self.kwargs))
    
class BookmarkCreateUpdateMixin(SuccessMessageMixin, SetCancelUrlMixin, BookmarkMixin):
    form_class = BookmarkForm

    def get_form_kwargs(self):
        menu =  _get_bookmarks(self.request, *self.args, **self.kwargs)
        kwargs = super(BookmarkCreateUpdateMixin, self).get_form_kwargs()
        kwargs['menu'] = menu
        return kwargs        
    
    def get_initial(self):
        initial = super(BookmarkCreateUpdateMixin, self).get_initial() 
        url = clean_http_referer(self.request)
        
        self.cancel_url = url
        
        if not self.object:
            initial["url"] = url
                
        return initial
    
class ListBookmarkView(BookmarkMixin, ModelListView):
    field_list = ["title", "url", "description", "new_window"]
    delete_template_name = "menus/bookmark_model_list_confirm_delete.html"
    paginate_by=10
    
    @method_decorator(permission_required("menus.view_menu", _get_bookmarks))
    def dispatch(self, request, *args, **kwargs):
        return super(ListBookmarkView, self).dispatch(request, *args, **kwargs)
    
class CreateBookmarkView(BookmarkCreateUpdateMixin, CreateView):
    success_message = _("The bookmark was created successfully.")
    
    @method_decorator(permission_required("menus.change_menu", _get_bookmarks))
    @method_decorator(permission_required("menus.add_link"))
    def dispatch(self, request, *args, **kwargs):
        return super(CreateBookmarkView, self).dispatch(request, *args, **kwargs)
    
class UpdateBookmarkView(BookmarkCreateUpdateMixin, UpdateView):
    success_url = reverse_lazy("bookmark_list")
    success_message = _("The bookmark was updated successfully.")
    
    @method_decorator(permission_required("menus.change_menu", _get_bookmarks))
    @method_decorator(permission_required("menus.change_link", _get_bookmark))
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateBookmarkView, self).dispatch(request, *args, **kwargs)
        
class DeleteBookmarkView(SuccessMessageMixin, SetCancelUrlMixin, BookmarkMixin, DeleteView):
    success_url = reverse_lazy("bookmark_list")
    success_message = _("The bookmark was deleted successfully.")
    
    @method_decorator(permission_required("menus.change_menu", _get_bookmarks))
    @method_decorator(permission_required("menus.delete_link", _get_bookmark))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteBookmarkView, self).dispatch(request, *args, **kwargs)
