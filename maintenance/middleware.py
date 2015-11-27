from django.conf import settings
from django.http import HttpResponseRedirect
from importlib import import_module
from maintenance import api
import logging

logger = logging.getLogger("maintenance.middleware")

class MaintenanceMiddleware(object):

    def __init__(self):
        try:
            self.setting_value = settings.MAINTENANCE_BYPASS_COOKIE
        except AttributeError:
            self.setting_value = None

    def redirect(self, status):
        logger.info('Maintenance Mode: Status %s. Redirect to %s' % (status, api.MAINTENANCE_URL))
        return HttpResponseRedirect(api.MAINTENANCE_URL)

    def process_request(self, request):
        if api.MAINTENANCE_URL == request.path:
            return None

        if request.path in api.BYPASSED_URLS:
            return None

        bypass_value = request.COOKIES.get('django_maintenance_bypass_cookie')

        if bypass_value and self.setting_value and \
                bypass_value == self.setting_value:
            return None

        status = api.status()

        if status == api.STATUS.OFFLINE:
            return self.redirect(api.STATUS.OFFLINE)

        if  status == api.STATUS.PENDING:
            engine = import_module(settings.SESSION_ENGINE)
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
            session = engine.SessionStore()
            if session.exists(session_key):
                return None
            else:
                return self.redirect(api.STATUS.PENDING)

        return None
