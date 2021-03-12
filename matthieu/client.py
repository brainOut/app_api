import requests
import sys
import getopt
import json


class PentesterApiClient():

    def __init__(self, url="http://localhost:8000"):
        self.__url = url
        self.__token = None
        self.__project = None
        self.__results = None
        self.error = None

    def __auth(self, username, passwd):
        try:
            r = requests.get(f"{self.__url}/auth", auth=requests.auth.HTTPBasicAuth(
                username, passwd))
        except (requests.HTTPError, requests.RequestException) as e:
            self.error = e
        else:
            if r.status_code == 200:
                self.__token = r.json()["token"]
            else:
                self.error = r.status_code


    def __get_project(self, project_token):
        try:
            r = requests.get(
                f"{self.__url}/project/{project_token}",
                headers={
                    "Content-Type": "application/json",
                    "x-access-tokens": self.__token
                })
        except (requests.HTTPError, requests.RequestException) as e:
            self.error = e
        else:
            if r.status_code == 200:
                self.__project = r.json()
            else:
                self.error = r.status_code

    def __launch(self, project_token, to_test):
        try:
            r = requests.post(
                f"{self.__url}/launch/{project_token}",
                data=json.dumps({"to_test": to_test}),
                headers={
                    "Content-Type": "application/json",
                    "x-access-tokens": self.__token
                })
        except (requests.HTTPError, requests.RequestException) as e:
            self.error = e
        else:
            if r.status_code == 200:
                self.__results = r.json()
            else:
                self.error = r.status_code

    def launch(self, usr, pwd, tk, tests):
        self.__auth(usr, pwd)
        if not self.error:
            self.__get_project(tk)
        if not self.error:
            self.__launch(tk, tests)
        return self.__results


if __name__ == "__main__":
    try:
        optlist, args = getopt.getopt(sys.argv[1:], None, ["user=", "passwd=", "token=", "tests="])
        user, passwd, token, tests = list(dict(optlist).values())
    except (getopt.GetoptError, ValueError, OSError) as e:
        sys.exit(e)
    api = PentesterApiClient()
    results = api.launch(user, passwd, token, tests.split(","))
    print(results)
    if any(results.values()):
        sys.exit(1)

