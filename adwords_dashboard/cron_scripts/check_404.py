import urllib.request
import urllib.error
from multiprocessing.pool import ThreadPool
import time
import re


class Check404(object):
    """
    Class for checking the response code of a urls
    @param: list of urls
    """

    seen = {}

    def __init__(self, urls):

        if not isinstance(urls, list):
            raise TypeError("Incorrect type, list required")

        self.urls = urls
        self.elapsed_time = 0

    @staticmethod
    def validate_url(url):

        regx = r'^http:\/\/\S*\..*|https:\/\/\S*\..*'

        if re.match(regx, url):
            return True

        return False

    def __check_url(self, dict_info):

        url = dict_info['Link']
        if not self.seen.get(url):
            try:
                code = urllib.request.urlopen(url).getcode()
                dict_info['code'] = code
                self.seen[url] = code
            except urllib.error.HTTPError as e:

                if hasattr(e, 'code'):
                        dict_info['code'] = e.code
                        self.seen[url] = e.code
                else:
                        dict_info['code'] = e
                        self.seen[url] = e
                return dict_info
            except KeyboardInterrupt:
                print("Keyboard Interrupt")
        else:
            dict_info['code'] = self.seen.get(url)

        return dict_info

    def get_results(self):

        init_time = time.time()
        data = []
        pool = ThreadPool(processes=2)
        results = [pool.apply_async(self.__check_url, (url,)) for url in self.urls]

        for res in results:
            try:
                data.append(res.get())
            except ValueError:
                pass

        pool.close()
        self.elapsed_time = time.time() - init_time

        return data
