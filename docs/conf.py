import importlib.metadata

project = "Flask-Session"
author = "Pallets Community Ecosystem"
copyright = f"2014, {author}"
release = importlib.metadata.version("Flask-Session")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("http://docs.python.org/", None),
    "flask": ("http://flask.palletsprojects.com/", None),
    "werkzeug": ("http://werkzeug.palletsprojects.com/", None),
    "flask-sqlalchemy": ("http://flask-sqlalchemy.palletsprojects.com/", None),
}

html_theme = "alabaster"
html_theme_options = {
    "github_button": True,
    "github_user": "pallets-eco",
    "github_repo": "flask-session",
}
