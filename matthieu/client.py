import requests
import sys
import getopt


class PentesterApiClient():

    def __init__(self, url="http://localhost:8000"):
        self.__url = url
        self.__token = None
        self.__project = None
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

    def __get_tests(self, project_token):
        try:
            r = requests.get(
                f"{self.__url}/tests/{project_token}",
                headers={
                    "Content-Type": "application/json",
                    "x-access-tokens": self.__token
                })
        except (requests.HTTPError, requests.RequestException) as e:
            self.error = e
        if r.status_code == 200:
            self.__tests = r.json()

    def launch(self, usr, pwd, tk):
        self.__auth(usr, pwd)
        if not self.error:
            self.__get_project(tk)
        return self.__project


if __name__ == "__main__":
    try:
        optlist, args = getopt.getopt(sys.argv[1:], None, ["url=", "user=", "passwd=", "token="])
        user, passwd, token = list(dict(optlist).values())
    except (getopt.GetoptError, ValueError, OSError) as e:
        sys.exit(e)
    api = PentesterApiClient()
    data = api.launch(user, passwd, token)
    print(data)

