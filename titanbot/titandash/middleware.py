from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin

from titanauth.constants import AUTH_URL_EXCEPTIONS
from titanbootstrap.constants import BOOTSTRAP_URL_EXCEPTIONS


class AutoAuthenticationMiddleware(MiddlewareMixin):
    """
    AutoAuthenticationMiddleware is used to ensure that the "titan" user is properly
    used as the requests user variable. This user is used throughout the dashboard.
    """
    def __init__(self, get_response):
        super(AutoAuthenticationMiddleware, self).__init__(get_response=get_response)

        # Setup a list of exceptions that are used to either grab the titan user,
        # or completely ignore that database call.
        self.exceptions = AUTH_URL_EXCEPTIONS + BOOTSTRAP_URL_EXCEPTIONS
        self.get_response = get_response

    def process_request(self, request):
        if request.path not in self.exceptions:
            request.user = User.objects.get(username="titan")
