
# List of url exceptions for our middleware and context processors.
# Bootstrapping should work with a completely empty database with no
# migrations yet applied. Lazily loading our data is one part, and not
# loading it at all in some cases is another preventative measure.
BOOTSTRAP_URL_EXCEPTIONS = [
    "/bootstrap/",
    "/bootstrap/ajax/check_update",
    "/bootstrap/ajax/perform_update",
    "/bootstrap/ajax/perform_requirements",
    "/bootstrap/ajax/perform_node_packages",
    "/bootstrap/ajax/perform_migration",
    "/bootstrap/ajax/perform_cache",
    "/bootstrap/ajax/perform_static",
    "/bootstrap/ajax/perform_dependency"
]
