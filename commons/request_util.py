import requests


class RequestUtil:
    session = requests.Session()
    def get_request_url(self, **kwargs):
        res = RequestUtil.session.request(**kwargs)
        return res
        