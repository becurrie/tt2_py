from django.shortcuts import redirect

from titanauth.models.user_reference import ExternalAuthReference
from titandash.middleware import TitandashBaseMiddleware


class TitandashAuthenticationMiddleware(TitandashBaseMiddleware):
    """
    TitandashAuthenticationMiddleware is used to send requests to the external authentication
    backend to determine if a user has access to the dashboard.
    """
    def process_request(self, request):
        """
        Code executed for each request before the view (and later middleware) is called.
        """
        # No user has been set yet, redirect to the login page and setup an empty user
        # that will be used for any subsequent requests.
        if request.path not in self.exceptions:
            if not ExternalAuthReference.objects.valid():
                return redirect("authenticate")

        # Grabbing and returning the response using the default django get_response
        # implementation.
        return self.get_response(request)
