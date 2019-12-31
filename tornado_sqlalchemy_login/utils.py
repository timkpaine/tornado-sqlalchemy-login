try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
    ConnectionRefusedError = OSError
import logging
import requests
import tornado
import ujson


def parse_body(req, **fields):
    try:
        data = tornado.escape.json_decode(req.body)
    except ValueError:
        data = {}
    return data


def safe_get(path, data=None, cookies=None, proxies=None):
    try:
        resp = requests.get(path, data=data, cookies=cookies, proxies=proxies)
        return ujson.loads(resp.text)
    except ConnectionRefusedError:
        return {}
    except ValueError:
        logging.critical("route:{}\terror code: {}\t{}".format(path, resp.status_code, resp.text))
        raise


def safe_post(path, data=None, cookies=None, proxies=None):
    try:
        resp = requests.post(path, data=data, cookies=cookies, proxies=proxies)
        return ujson.loads(resp.text)
    except ConnectionRefusedError:
        return {}
    except ValueError:
        logging.critical("route:{}\nerror code: {}\t{}".format(path, resp.status_code, resp.text))
        raise


def safe_post_cookies(path, data=None, cookies=None, proxies=None):
    try:
        resp = requests.post(path, data=data, cookies=cookies, proxies=proxies)
        return ujson.loads(resp.text), resp.cookies
    except ConnectionRefusedError:
        return {}, None
    except ValueError:
        logging.critical("route:{}\nerror code: {}\t{}".format(path, resp.status_code, resp.text))
        raise


def construct_path(host, method):
    return urljoin(host, method)
