# coding=utf-8

from __future__ import absolute_import

from talos.core import utils
from talos.core.i18n import _
from talos.db import validator


class LengthValidator(validator.NullValidator):
    def __init__(self, minimum, maximum):
        self._minimum = minimum
        self._maximum = maximum

    def validate(self, value):
        if not utils.is_string_type(value):
            return _('expected string, not %(type)s ') % {'type': type(value).__name__}
        if self._minimum <= len(value) and len(value) <= self._maximum:
            return True
        return _('length required: %(min)d <= %(value)d <= %(max)d') % {
            'min': self._minimum,
            'value': len(value),
            'max': self._maximum
        }


class BackRefValidator(validator.NullValidator):
    def __init__(self, cls_res):
        self.cls_res = cls_res

    def validate(self, value):
        if self.cls_res().count(filters={'id': value}) == 0:
            return _('reference of %(resource)s(%(id)s) not found') % {'resource': self.cls_res.__name__, 'id': value}
        return True


TypeValidator = validator.TypeValidator


class RepeatableValidator(validator.NullValidator):
    def validate(self, value):
        choices = ['?', '+', '*']
        if utils.is_string_type(value):
            if value not in choices:
                return _('expected %(choices)s, not %(value)s') % {'choices': choices, 'value': value}
        elif isinstance(value, int):
            if value < 1:
                return _('value should be >= 1, not %(value)s') % {'value': value}
        else:
            return _('expected string in %(choices)s or int(>=1), not %(type)s ') % {
                'choices': choices,
                'type': type(value).__name__
            }
        return True
