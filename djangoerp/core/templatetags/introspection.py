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


from copy import copy
from django.conf import settings
from django.db import models
from django.utils.encoding import force_text
from django import template
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from djangoerp.core.utils.models import (
    get_model,
    get_fields,
    get_field_type,
)


register = template.Library()


@register.filter
def typeof(value):
    """Returns the type of the given value.

    Example usage: {{ my_var|typeof }}
    """
    return (u"%s" % type(value)).replace("<class '", "").replace("<type '", "").replace("'>", "")


@register.filter
def model_name(obj):
    """Returns the model name for the given instance.

    Example usage: {{ object|model_name }}
    """
    try:
        mk = get_model(obj)
        return force_text(mk._meta.verbose_name)
    except:
        pass
    return ""


@register.filter
def model_name_plural(obj):
    """Returns the pluralized model name for the given instance.

    Example usage: {{ object|model_name_plural }}
    """
    try:
        mk = get_model(obj)
        return force_text(mk._meta.verbose_name_plural)
    except:
        pass
    return ""


@register.filter
def raw_model_name(obj):
    """Returns the raw model name for the given instance.

    Example usage: {{ object|raw_model_name }}
    """
    try:
        mk = get_model(obj)
        return mk.__name__.lower()
    except:
        pass
    return ""


@register.filter
def raw_model_name_plural(obj):
    """Returns the raw pluralized model name for the given instance.

    Example usage: {{ object|raw_model_name_plural }}
    """
    name = raw_model_name(obj)
    if name:
        return u"%ss" % name
    return ""
