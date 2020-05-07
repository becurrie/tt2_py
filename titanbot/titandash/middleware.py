from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse


class TitandashBaseMiddleware(MiddlewareMixin):
    """
    Base Titandash middleware that performs the setup or urls that should be ignored when our
    requests are processed by the system.
    """
    def __init__(self, get_response):
        super(TitandashBaseMiddleware, self).__init__(get_response=get_response)
        self.exceptions = [
            # Titanauth.
            reverse("authenticate"),
            reverse("credentials"),
            #  Titan Bootstrap.
            reverse("check_update"),
            reverse("perform_update"),
            reverse("perform_requirements"),
            reverse("perform_node_packages"),
            reverse("perform_migration"),
            reverse("perform_cache"),
            reverse("perform_static"),
            reverse("perform_dependency")
        ]
        self.get_response = get_response


class AutoAuthenticationMiddleware(TitandashBaseMiddleware):
    """
    AutoAuthenticationMiddleware is used to ensure that the "titan" user is properly
    used as the requests user variable. This user is used throughout the dashboard.
    """
    def process_request(self, request):
        if request.path not in self.exceptions:
            request.user = User.objects.get(username="titan")
