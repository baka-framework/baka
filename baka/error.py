import traceback

import webob
from pyramid.httpexceptions import HTTPNotFound

from .response import JSONAPIResponse


def generic(context, request):
    settings = request.registry.settings
    with JSONAPIResponse(request.response) as resp:
        _in = u'Failed'
        code, status = JSONAPIResponse.INTERNAL_SERVER_ERROR
        request.response.status_int = code
        try:
            message = {'message': context.args[0]}
        except IndexError:
            message = {'message': 'Unknown error'}
        if settings.get('baka.debug', True):
            message['traceback'] = ''.join(
                traceback.format_exception(*request.exc_info))
    return resp.to_json(
        _in, code=code,
        status=status, message=message)


def http_error(context, request):
    with JSONAPIResponse(request.response) as resp:
        _in = u'Failed'
        code, status = JSONAPIResponse.BAD_REQUEST
        if isinstance(context, webob.Response) \
                and context.content_type == 'application/json':
            return context

        request.response.status = context.status
        status = context.status
        for (header, value) in context.headers.items():
            if header in {'Content-Type', 'Content-Length'}:
                continue
            request.response.headers[header] = value
        if context.message:
            message =  {'message': context.message}
        else:
            message = {'message': context.status}

    return resp.to_json(
        _in, code=code,
        status=status, message=message)


def notfound(context, request):
    with JSONAPIResponse(request.response) as resp:
        _in = u'Failed'
        code, status = JSONAPIResponse.NOT_FOUND
        request.response.status_int = code
        message = 'Resource not found'
        if isinstance(context, HTTPNotFound):
            if context.content_type == 'application/json':
                return context
            elif context.detail:
                message = context.detail

    return resp.to_json(
        _in, code=code,
        status=status, message=message)


def forbidden(request):
    with JSONAPIResponse(request.response) as resp:
        _in = u'Failed'
        if request.unauthenticated_userid:
            code, status = JSONAPIResponse.FORBIDDEN
            request.response.status_int = code
            message = {'message': 'You are not allowed to perform this action.'}
        else:
            code, status = JSONAPIResponse.NOT_AUTHORIZED
            request.response.status_int = code
            message = {'message': 'You must login to perform this action.'}

    return resp.to_json(
        _in, code=code,
        status=status, message=message)