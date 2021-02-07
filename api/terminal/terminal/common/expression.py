# coding=utf-8
"""
terminal.common.expression
~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供WeCube通用表达式解析

"""
import json
import re

from terminal.common import exceptions

R_SINGLE_FILTER = re.compile(r'\{([_a-zA-Z][_a-zA-Z0-9.]*)\s+([a-zA-Z]+)\s+([^}]+)\}')
R_SEG_EXPRESSION = re.compile(
    r'(?:\(([_a-zA-Z][_a-zA-Z0-9]*)\))?(?:([_a-zA-Z][_a-zA-Z0-9]*):)([_a-zA-Z][_a-zA-Z0-9]*)((?:\{[_a-zA-Z][_a-zA-Z0-9.]*\s+[a-zA-Z]+\s+.*\}){1,30})?(?:\.([_a-zA-Z][_a-zA-Z0-9]*))?$'
)


def _expr_op_finder(expr):
    '''
    find all indexes of operators
    :param expr: expression
    '''
    results = []
    ops = ['~', '>', '->', '<-']
    for el in ops:
        index = expr.find(el)
        if index != -1:
            if el == '>' and expr[index - 1] == '-':
                # ignore it, we will find it when op = '->'
                pass
            else:
                results.append({'op': el, 'index': index})
        while index != -1:
            index = expr.find(el, index + len(el))
            if index != -1:
                if el == '>' and expr[index - 1] == '-':
                    # ignore it, we will find it when op = '->'
                    pass
                else:
                    results.append({'op': el, 'index': index})
    results.sort(key=lambda x: x['index'])
    return results


def _expr_split(expr, indexes):
    '''
    split expr according to indexes
    :param expr: expression
    :param indexes: result of _expr_op_finder
    '''
    results = []
    start = 0
    for el in indexes:
        results.append({'type': 'expr', 'value': expr[start:el['index']], 'data': None})
        results.append({'type': 'op', 'value': el['op'], 'data': None})
        start = el['index'] + len(el['op'])
    results.append({'type': 'expr', 'value': expr[start:], 'data': None})
    return results


def expr_filter_parse(expr_filter):
    '''
    parse filter to dict, eg. "{key1 op val1}{...}"
    :param expr_filter: filter expression
    '''
    results = []
    if len(expr_filter) > 0:
        index = 0
        while index < len(expr_filter):
            res = R_SINGLE_FILTER.match(expr_filter, index)
            if res:
                filter_name = res.groups()[0]
                filter_op = res.groups()[1]
                filter_val = res.groups()[2]
                if filter_op == 'is':
                    filter_op = 'null'
                    filter_val = None
                elif filter_op == 'isnot':
                    filter_op = 'notnull'
                    filter_val = None
                elif filter_op == 'set':
                    filter_val = None
                elif filter_op == 'notset':
                    filter_val = None
                elif filter_op in ('in', 'notin', 'nin'):
                    # TODO: fix this, replace is not good enough
                    filter_val = json.loads(filter_val.replace("'", '"'))
                elif (filter_val.startswith("'") and filter_val.endswith("'")) or (filter_val.startswith('"')
                                                                                   and filter_val.endswith('"')):
                    # string
                    filter_val = filter_val[1:-1]
                else:
                    # number
                    rule_float = '^\d+\.\d+$'
                    if re.match(rule_float, filter_val):
                        filter_val = float(filter_val)
                    else:
                        filter_val = int(filter_val)

                results.append({'name': filter_name, 'operator': filter_op, 'value': filter_val})
                index = res.end()
            else:
                index = len(expr_filter)
    return results


def expr_seg_parse(expr):
    '''
    parse a segment of expression to dict, eg. "(attr)[plugin:]ci[{key op value}*][.attr]" into
    {
        'backref_attribute': '',
        'plugin': '',
        'ci': '',
        'filters': '',
        'attribute': ''
    }
    :param expr_filter: expression
    '''
    res = R_SEG_EXPRESSION.match(expr)
    if res:
        result = {
            'expr': expr,
            'backref_attribute': res.groups()[0] or '',
            'plugin': res.groups()[1] or '',
            'ci': res.groups()[2] or '',
            'filters': res.groups()[3] or '',
            'attribute': res.groups()[4] or ''
        }
        result['filters'] = expr_filter_parse(result['filters'])
        return result
    raise exceptions.PluginError('invalid expression: ' + expr)


def expr_parse(expr):
    '''
    parse an expression to dict
    :param expr: expression
    '''
    split_res = _expr_split(expr, _expr_op_finder(expr))
    for el in split_res:
        if el['type'] == 'expr':
            el['data'] = expr_seg_parse(el['value'])
    return split_res
