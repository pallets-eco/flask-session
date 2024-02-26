import importlib.metadata

project = "Flask-Session"
author = "Pallets Community Ecosystem"
copyright = f"2014, {author}"
version = release = importlib.metadata.version("Flask-Session")

# General --------------------------------------------------------------

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "sphinx_favicon"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "flask": ("https://flask.palletsprojects.com/", None),
    "werkzeug": ("https://werkzeug.palletsprojects.com/", None),
    "flask-sqlalchemy": ("https://flask-sqlalchemy.palletsprojects.com/", None),
    "redis": ("https://redis-py.readthedocs.io/en/stable/", None),
}


# HTML -----------------------------------------------------------------

favicons = [
    {"rel": "icon", "href": "icon.svg", "type": "image/svg+xml"},
    {"rel": "icon", "sizes": "16x16", "href": "favicon-16x16.png", "type": "image/png"},
    {"rel": "icon", "sizes": "32x32", "href": "favicon-32x32.png", "type": "image/png"},
    {"rel": "icon", "sizes": "48x48", "href": "favicon-48x48.png", "type": "image/png"},
    {
        "rel": "icon",
        "sizes": "192x192",
        "href": "favicon-192x192.png",
        "type": "image/png",
    },
    {
        "rel": "icon",
        "sizes": "512x512",
        "href": "favicon-512x512.png",
        "type": "image/png",
    },
    {
        "rel": "apple-touch-icon",
        "sizes": "180x180",
        "href": "apple-touch-icon-180x180.png",
        "type": "image/png",
    },
    {
        "rel": "mask-icon",
        "href": "safari-pinned-tab.svg",
    },
]
html_copy_source = False
html_css_files = [
    "styles.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
]
html_domain_indices = False
html_static_path = ["_static"]
html_theme = "furo"
html_theme_options = {
    "announcement": "Flask-Session is switching serializer to msgspec in 1.0.0. Version 0.7.0 will migrate existing sessions upon read or write.",
    "source_repository": "https://github.com/pallets-eco/flask-session/",
    "source_branch": "main",
    "source_directory": "docs/",
    "light_logo": "logo/logo-light.png",
    "dark_logo": "logo/logo-dark.png",
    "light_css_variables": {
        "font-stack": "'Atkinson Hyperlegible', sans-serif",
        "font-stack--monospace": "'Source Code Pro', monospace",
        "color-brand-primary": "#39A9BE",
        "color-brand-content": "#39A9BE",
    },
    "dark_css_variables": {
        "font-stack": "'Atkinson Hyperlegible', sans-serif",
        "font-stack--monospace": "'Source Code Pro', monospace",
        "color-brand-primary": "#39A9BE",
        "color-brand-content": "#39A9BE",
    },
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/pallets-eco/flask-session",
            "html": "",
            "class": "fa-brands fa-solid fa-github fa-lg",
        },
        {
            "name": "Discord",
            "url": "https://discord.gg/pallets",
            "html": "",
            "class": "fa-brands fa-solid fa-discord fa-lg",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/Flask-Session/",
            "html": "",
            "class": "fa-brands fa-solid fa-python fa-lg",
        },
    ],
}
html_use_index = False
