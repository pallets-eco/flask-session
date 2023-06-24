class TestMemcached:
    """This requires package: memcached
       This needs to be running before test runs
    """
    def test_basic(self, app_utils):
        app = app_utils.create_app({'SESSION_TYPE': 'memcached'})
        app_utils.test_session_set(app)