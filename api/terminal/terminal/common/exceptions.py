# coding=utf-8
"""
terminal.common.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供项目定义异常

"""

from talos.core.i18n import _
from talos.core import exceptions as core_ex


class PluginError(core_ex.Error):
    """基础异常"""
    code = 200
    error_code = 40000

    def __init__(self, message=None, exception_data=None, **kwargs):
        exception_data = exception_data or {}
        exception_data['error_code'] = self.error_code
        super(PluginError, self).__init__(message, exception_data=exception_data, **kwargs)

    def set_error_code(self, code):
        self._exception_data['error_code'] = code
        return self

    @property
    def title(self):
        return _('Plugin Business Processing Error')


class FieldRequired(PluginError):
    """字段缺失异常"""
    code = 200
    error_code = 40001

    @property
    def title(self):
        return _('Field Missing')

    @property
    def message_format(self):
        return _('column: %(attribute)s must be specific')


class ValidationError(PluginError):
    """数据校验异常"""
    code = 200
    error_code = 40002

    @property
    def title(self):
        return _('Validation Error')

    @property
    def message_format(self):
        return _('column %(attribute)s validate failed, because: %(msg)s')


class PluginCallError(PluginError):
    """系统间调用异常"""
    code = 200
    error_code = 40003


class NotFoundError(PluginError):
    """查找系统间数据异常"""
    code = 200
    error_code = 40004

    @property
    def message_format(self):
        return _('the resource(%(resource)s) you request not found')


class BatchPartialError(PluginError):
    """批量数据操作异常"""
    code = 200
    error_code = 40005

    @property
    def title(self):
        return _('Batch Operation Partial Error')

    @property
    def message_format(self):
        return _('fail to %(action)s [%(num)s] record, detail error in the data block')


class ConflictError(PluginError):
    """约束冲突错误异常"""
    code = 200
    error_code = 40009

    @property
    def title(self):
        return _('Conflict')

    @property
    def message_format(self):
        return _('object[%(oid)s] is used by %(name)s')
