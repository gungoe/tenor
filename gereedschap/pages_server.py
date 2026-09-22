"""Een servertje dat Cache-Control: max-age=600 meestuurt, zoals GitHub Pages.
   Gebruik: python3 gereedschap/pages_server.py 8765 <map>"""
import functools, http.server, sys


class Pages(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'max-age=600')
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    poort, map_ = int(sys.argv[1]), sys.argv[2]
    http.server.ThreadingHTTPServer(('localhost', poort), functools.partial(Pages, directory=map_)).serve_forever()
