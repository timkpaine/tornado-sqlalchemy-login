from mock import MagicMock, patch
from tornado_sqlalchemy_login.utils import parse_body, construct_path, safe_get, safe_post, safe_post_cookies


def foo(*args, **kwargs):
    raise ConnectionRefusedError()


class TestUtils:
    def test_parse_body(self):
        m = MagicMock()
        m.body = '{}'
        parse_body(m)
        m.body = ''
        parse_body(m)

    def test_constructPath(self):
        assert(construct_path('test', 'test') == 'test')

    def test_safe_get(self):
        with patch('requests.get') as m:
            m.return_value = MagicMock()
            m.return_value.text = '{}'
            assert safe_get('test') == {}

            m.side_effect = foo
            assert safe_get('test') == {}

    def test_safe_post(self):
        with patch('requests.post') as m:
            m.return_value = MagicMock()
            m.return_value.text = '{}'
            assert safe_post('test') == {}

            m.side_effect = foo
            assert safe_post('test') == {}

    def test_safe_post_cookies(self):
        with patch('requests.post') as m:
            m.return_value = MagicMock()
            m.return_value.text = '{}'
            assert safe_post_cookies('test')[0] == {}

            m.side_effect = foo
            assert safe_post_cookies('test')[0] == {}
