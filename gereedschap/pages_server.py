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
    server = http.server.ThreadingHTTPServer(('127.0.0.1', poort), functools.partial(Pages, directory=map_))
    print(f'luistert op {poort}', flush=True)   # het teken voor omgeving.start_server: deze server, niet een andere
    server.serve_forever()
