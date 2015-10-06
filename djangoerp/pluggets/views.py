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


import json

from django.db.models import Model as DjangoModel
from django.forms import Form as DjangoForm
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from formtools.wizard.views import SessionWizardView
from djangoerp.core.views import SetCancelUrlMixin
from djangoerp.core.decorators import obj_permission_required as permission_required

from .loading import registry
from .decorators import is_plugget_editable
from .models import *
from .forms import *


def _get_plugget(*args, **kwargs):
    """Returns the plugget instance associated to the "pk" kwarg, None otherwise.
    """
    try:
        return Plugget.objects.get(pk=kwargs.get("pk", None))
    except Plugget.DoesNotExist:
        return None

def _get_plugget_add_or_edit_perm(*args, **kwargs):
    """Returns the permission that should be checked.
    
    If a "pk" kwarg is present, we're checking for edit an existing plugget,
    otherwise we want to add a new one.
    """
    plugget = _get_plugget(*args, **kwargs)
    if plugget:
        return "pluggets.change_plugget"
    return "pluggets.add_plugget"

def _get_region(*args, **kwargs):
    """Returns the region instance associated to the "slug" kwarg.
    
    If there is no "slug" argument, it tries to retrieve the region from one of
    its plugget (using the "pk" kwarg, if present).
    
    If also this fails, it raises an exception.
    """
    default = _get_plugget(*args, **kwargs)
    if default:
        default = default.region.slug
    return Region.objects.get(slug=kwargs.get("slug", default))

class PluggetWizard(SetCancelUrlMixin, SessionWizardView):
    DEFAULT_FORMS = [SelectPluggetSourceForm, CustomizePluggetSettingsForm]
    template_name = "pluggets/plugget_wizard_form.html"
    model = Plugget
    instance = None
    source = None
    region = None
    
    @method_decorator(permission_required("pluggets.change_region", _get_region))
    @method_decorator(permission_required(_get_plugget_add_or_edit_perm, _get_plugget))
    @method_decorator(is_plugget_editable(_get_plugget))
    def dispatch(self, request, *args, **kwargs):
        return super(PluggetWizard, self).dispatch(request, *args, **kwargs)
        
    def get_form_kwargs(self, step):
        if "pk" in self.kwargs:
            self.instance = get_object_or_404(Plugget, pk=self.kwargs['pk'])
            self.region = self.instance.region
            
        elif "slug" in self.kwargs:
            self.region = get_object_or_404(Region, slug=self.kwargs['slug'])
            
        if step == "1":
            return {"region": self.region}
            
        return {}
        
    def get_form(self, step=None, data=None, files=None):
        form = super(PluggetWizard, self).get_form(step, data, files)

        # determine the step if not given
        if step is None:
            step = self.steps.current

        if step == '1':
            custom_form_class = self.source['form']
            if custom_form_class and issubclass(custom_form_class, DjangoForm):
                custom_form = custom_form_class(self.get_form_initial(step))
                form.fields.update(custom_form.fields)
            
        return form
        
    def get_form_instance(self, step):
        if step == '1':
            return self.instance
        return self.instance_dict.get(step, None)
    
    def get_form_initial(self, step):
        initial = super(PluggetWizard, self).get_form_initial(step)
        source_uid = None
        title = None
        
        data0 = self.storage.get_step_data("0")
        data1 = self.storage.get_step_data("1")
        sources = registry.get_plugget_sources()
        
        if self.instance:
            source_uid = self.instance.source
            title = self.instance.title
            if data0:
                source_uid = data0.get('0-source_uid', self.instance.source)
            self.source = sources.get(source_uid, {})
            self.source['source_uid'] = source_uid
            if data1:
                title = data1.get('1-title', self.instance.title)
            
        else:
            if data0:
                source_uid = data0.get('0-source_uid', None)
            self.source = sources.get(source_uid, {})
            self.source['source_uid'] = source_uid
            if data1:
                title = data1.get('1-title', source_uid)

        if step == "0":
            initial['region_slug'] = self.region.slug
            initial['source_uid'] = source_uid
                
        elif step == "1":
            initial['title'] = title or source_uid
            if self.instance:
                initial.update(json.loads(self.instance.context or "{}"))
                
        self.cancel_url = self.region.get_absolute_url()
            
        return initial
        
    def get_context_data(self, form, **kwargs):
        context = super(PluggetWizard, self).get_context_data(form=form, **kwargs)
        context.update({'object': self.instance, 'region': self.region})
        if self.steps.current == '1':
            context.update({
                "plugget_description": self.source['description'],
            })
        return context
            
    def done(self, form_list, **kwargs):
        from django.http import HttpResponseRedirect
        
        # First step:
        f0 = form_list[0]
        
        source_uid = f0.cleaned_data['source_uid']
        source = registry.get_plugget_source(source_uid)
        
        # Second step:
        f1 = form_list[1]
            
        title = f1.cleaned_data['title']
        context = {}
        
        for k, v in list(f1.cleaned_data.items()):
            if k != "title":
                context[k] = v
                if isinstance(v, DjangoModel):
                    context[k] = v.pk
                
        context = json.dumps(context)
        
        # Merging:
        if self.instance:
            self.instance.source = source_uid
            self.instance.title = title
            self.instance.context = context
            self.instance.template = source['default_template']
            self.instance.description = source['description']
            self.instance.save()
            messages.success(self.request, _("The plugget was updated successfully."))
        
        else:
            region = get_object_or_404(Region, slug=kwargs.get('slug', None))
            self.instance = Plugget.objects.create(
                source=source_uid,
                region=region,
                title=title,
                context=context,
                description=source['description'],
                template=source['default_template'],
                sort_order=region.pluggets.count()
            )
            messages.success(self.request, _("The plugget was created successfully."))
            
        return HttpResponseRedirect(self.instance.get_absolute_url())
        
class DeletePluggetView(SuccessMessageMixin, SetCancelUrlMixin, DeleteView):
    model = Plugget
    success_message = _("The plugget was deleted successfully.")
    
    @method_decorator(permission_required("pluggets.change_region", _get_region))
    @method_decorator(permission_required("pluggets.delete_plugget", _get_plugget))
    def dispatch(self, request, *args, **kwargs):
        return super(DeletePluggetView, self).dispatch(request, *args, **kwargs)
        
    def get_object(self, queryset=None):
        self.object = super(DeletePluggetView, self).get_object(queryset)
        self.cancel_url = self.object.region.get_absolute_url()
        self.success_url = self.object.region.get_absolute_url()
        return self.object
