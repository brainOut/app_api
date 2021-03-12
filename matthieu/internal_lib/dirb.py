import requests
from bs4 import BeautifulSoup
from pathlib import Path


def have_inputs(url):
    html = requests.get(url, headers={
        "User-Agent": "Chocapic/3.0"}).content
    html_bs4 = BeautifulSoup(html, 'html.parser')
    html_inputs = html_bs4.findAll('input')

    if len(html_inputs) != 0:
        return True
    else:
        return False


def save_or_return(save_outputs, data, file_name):
    if save_outputs:
        open('results/'+file_name, 'w').write("\r\n".join(data))

    return data


class FuzzUrl:

    def __init__(self, url, quiet=False):
        """params url : Url to fetch, quiet: True or False (print or not results)"""
        self.url = url
        self.quiet = quiet
        with open(Path("internal_lib/wordlist").absolute() / "url_fuzzer.txt", 'r') as f:
            self.wordlist = f.readlines()

    def dirchecker(self, with_inputs_only=False, save_outputs=False, filename='chocapic.txt'):
        url_ok = []
        url_with_inputs = []
        for paths in self.wordlist:
            paths = paths.strip("\r\n")
            try:
                url = f"{self.url}/{paths}" if self.url.startswith('http://') else f"http://{self.url}/{paths}"
                r = requests.get(url)
                if not self.quiet:
                    print(f"trying {url}")
                if r.status_code != 404:
                    url_ok.append(url)
            except Exception:
                exit(f"Can't reach the host {self.url}")

        if with_inputs_only:
            for url in url_ok:
                if have_inputs(url):
                    url_with_inputs.append(url)

            save_or_return(save_outputs, url_with_inputs, filename)
        else:
            save_or_return(save_outputs, url_ok, filename)


if __name__ == "__main__":
    fuzzer = FuzzUrl('127.0.0.1:8000', True)
    fuzzer.dirchecker(True, True)


# TODO :
# 1 - Fuzz url (fait)
# 2 - scrap de source à la recherche de formulaire (fait)
# 3 - tentatives de SQLI (à l'aide sqlmap, pas inclut dans le script)
# 4 - Si sqli OK --> prend les hash et on les crack
# 5 - Si Sqli KO --> Bruteforce id /pass (rockyou.txt)
# 6 - Sniff (coke.py) nécessite une backdoor
