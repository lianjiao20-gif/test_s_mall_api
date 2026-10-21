import requests


class RequestUtil:

    def getSession(self):
        return requests.Session()
    
    def sendRequest(self, **kwargs):
        res = self.getSession().request(**kwargs)
        return res
        