"""
Flask-Session
-------------

Description goes here...

Links
`````

* `documentation <http://packages.python.org/Flask-Session>`_
* `development version
  <http://github.com/USERNAME/REPOSITORY/zipball/master#egg=Flask-Session-dev>`_

"""
from setuptools import setup


setup(
    name='Flask-Session',
    version='0.1',
    url='<enter URL here>',
    license='BSD',
    author='Shipeng Feng',
    author_email='your-email-here@example.com',
    description='<enter short description here>',
    long_description=__doc__,
    packages=['flask_session'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.8'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
