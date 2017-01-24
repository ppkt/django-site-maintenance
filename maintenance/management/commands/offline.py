import datetime
from django.contrib.sessions.models import Session
from django.core.management.base import CommandError, BaseCommand
import time
import maintenance.api as api
import logging

logger = logging.getLogger("maintenance")


class Command(BaseCommand):

    def add_arguments(self, parser):
        """
        :param argparse.ArgumentParser parser:
        :return:
        """
        parser.add_argument('command', choices=[
            'on', 'off', 'check', 'list', 'activate', 'deactivate', 'status'])

        parser.add_argument(
            '--force', action='store_true', dest='ignore_session',
            default=False, help='Do not wait for active session. '
                                'Brutally disconnect users')
        parser.add_argument(
            '--timeout', action='store', dest='timeout', default=60,
            help='Time to wait for pending sessions')

    def handle(self, *labels, **options):
        cmd = options.get('command')
        verbosity = options.get('verbosity')
        timeout = options.get('timeout')
        ignore_session = options.get('ignore_session')
        ret, msg = 0, 'Unknown error'

        if cmd in ('check', 'status'):
            ret, msg = api.check()
            print msg
        elif cmd in ('on', 'activate'):
            ret, msg = api.start(ignore_session, timeout, verbosity)
            if verbosity >= 1:
                print msg
        elif cmd in ('off', 'deactivate'):
            ret, msg = api.stop()
            if verbosity >= 1:
                print msg
        elif cmd in ('list',):
            now = datetime.datetime.now()
            for s in Session.objects.filter(expire_date__gte=now):
                offset = (time.mktime(s.expire_date.timetuple()) -
                          time.mktime(now.timetuple()))
                print s.pk, s.expire_date, offset
        if ret:
            raise CommandError(msg)
