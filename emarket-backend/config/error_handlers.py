"""
Custom Error Handlers for Marketplace
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def bad_request(request, exception=None):
    """
    Handler for 400 Bad Request
    """
    if request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'error',
            'error': {
                'code': 'bad_request',
                'message': str(exception) if exception else _('Bad request.'),
            }
        }, status=400)
    
    return render(request, 'errors/400.html', {
        'error_code': 400,
        'error_message': _('Bad Request'),
        'error_description': str(exception) if exception else _('The request was invalid.'),
    }, status=400)


def permission_denied(request, exception=None):
    """
    Handler for 403 Forbidden
    """
    if request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'error',
            'error': {
                'code': 'permission_denied',
                'message': str(exception) if exception else _('Permission denied.'),
            }
        }, status=403)
    
    return render(request, 'errors/403.html', {
        'error_code': 403,
        'error_message': _('Permission Denied'),
        'error_description': str(exception) if exception else _('You do not have permission to access this resource.'),
    }, status=403)


def page_not_found(request, exception=None):
    """
    Handler for 404 Not Found
    """
    if request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'error',
            'error': {
                'code': 'not_found',
                'message': _('Resource not found.'),
                'path': request.path,
            }
        }, status=404)
    
    return render(request, 'errors/404.html', {
        'error_code': 404,
        'error_message': _('Page Not Found'),
        'error_description': _('The requested resource was not found on this server.'),
        'path': request.path,
    }, status=404)


def server_error(request):
    """
    Handler for 500 Internal Server Error
    """
    if request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'error',
            'error': {
                'code': 'internal_server_error',
                'message': _('Internal server error. Please try again later.'),
            }
        }, status=500)
    
    return render(request, 'errors/500.html', {
        'error_code': 500,
        'error_message': _('Internal Server Error'),
        'error_description': _('Something went wrong on our end. Please try again later.'),
    }, status=500)