from django.utils.functional import SimpleLazyObject

from titanauth.models.user_reference import ExternalAuthReference
from titanauth.authentication.constants import AUTH_ACCOUNT_URL


def login(request):
    """
    Include the current external auth reference in template contexts.
    """
    def _login_query():
        """
        Use callable to lazily grab information needed.
        """
        dct = {}

        try:
            dct["auth"] = ExternalAuthReference.objects.all().first()
        except Exception:
            dct["auth"] = None

        dct["auth_account"] = AUTH_ACCOUNT_URL
        return dct

    return SimpleLazyObject(_login_query)

