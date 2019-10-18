
# List of url exceptions for our middleware and context processors.
# Bootstrapping should work with a completely empty database with no
# migrations yet applied. Lazily loading our data is one part, and not
# loading it at all in some cases is another preventative measure.
AUTH_URL_EXCEPTIONS = [
    "/auth/authenticate",
    "/auth/ajax/credentials"
]
