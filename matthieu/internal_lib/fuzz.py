from boofuzz import *


class Fuzz:
    def __init__(self, url="127.0.0.1", port=80):
        self.url = url
        self.port = port

    def fuzz_http(self):
        session = Session(
                target=Target(connection=TCPSocketConnection(self.url, self.port)),
            )

        s_initialize(name="Request")
        with s_block("Request-Line"):
            s_group("Method", ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"])
            s_delim(" ", name="space-1")
            s_string("/index.html", name="Request-URI")
            s_delim(" ", name="space-2")
            s_string("HTTP/1.1", name="HTTP-Version")
            s_static("\r\n", name="Request-Line-CRLF")
            s_string("Host:", name="Host-Line")
            s_delim(" ", name="space-3")
            s_string("example.com", name="Host-Line-Value")
            s_static("\r\n", name="Host-Line-CRLF")
            s_static("Content-Length:", name="Content-Length-Header")
            s_delim(" ", name="space-4")
            s_size("Body-Content", output_format="ascii", name="Content-Length-Value")
            s_static("\r\n", "Content-Length-CRLF")
        s_static("\r\n", "Request-CRLF")

        with s_block("Body-Content"):
            s_string("Body content ...", name="Body-Content-Value")

        session.connect(s_get("Request"))

        session.fuzz()


# def basic():
#     session = Session(
#         target=Target(
#             connection=TCPSocketConnection("192.168.1.71", 21)))
#
#     s_initialize("user")
#     s_string("USER")
#     s_delim(" ")
#     s_string("user2")
#     s_static("\r\n")
#
#     s_initialize("pass")
#     s_string("PASS")
#     s_delim(" ")
#     s_string("passwd")
#     s_static("\r\n")
#
#     s_initialize("stor")
#     s_string("STOR")
#     s_delim(" ")
#     s_string("AAAA")
#     s_static("\r\n")
#
#     s_initialize("retr")
#     s_string("RETR")
#     s_delim(" ")
#     s_string("AAAA")
#     s_static("\r\n")
#
#     session.connect(s_get("user"))
#     session.connect(s_get("user"), s_get("pass"))
#     session.connect(s_get("pass"), s_get("stor"))
#     session.connect(s_get("pass"), s_get("retr"))
#
#     session.fuzz()
#
#


if __name__ == '__main__':
    # http()
    fuzz = Fuzz("127.0.0.1", 21)
    fuzz.fuzz_http(fuzz.url, fuzz.port)
