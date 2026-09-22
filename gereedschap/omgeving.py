"""Gedeelde paden en hulpjes voor het gereedschap. De repo is de map boven deze."""
import pathlib, shutil, socket, subprocess, sys, time

HIER = pathlib.Path(__file__).resolve().parent
REPO = HIER.parent
FIXTURES = REPO / 'test' / 'fixtures'
WERKMAP = HIER / 'werkmap'            # kijkbestanden en schermafdrukken; mag je altijd weggooien


def kijkbestanden(namen=('voorbeeld', 'rest', 'oud')):
    """Bouwt per fixture een los html-bestand met de gegevens erin, plus echt.html (de app zelf)."""
    WERKMAP.mkdir(exist_ok=True)
    for naam in namen:
        subprocess.run([sys.executable, str(HIER / 'maak_voorbeeld_html.py'), str(REPO / 'index.html'),
                        str(FIXTURES / f'{naam}.json'), str(WERKMAP / f'{naam}.html')], check=True)
    shutil.copy(REPO / 'index.html', WERKMAP / 'echt.html')
    return WERKMAP


def url(pad):
    return 'file://' + str(pad)


def kopie_van_de_app(doel):
    """Kopie van de app zonder gereedschap, om te serveren."""
    doel = pathlib.Path(doel)
    shutil.rmtree(doel, ignore_errors=True)
    shutil.copytree(REPO, doel, ignore=shutil.ignore_patterns('gereedschap', '.git', '__pycache__'))
    return doel


def start_server(map_, poort):
    """Start pages_server.py (met Cache-Control: max-age=600, zoals GitHub Pages) en wacht tot hij luistert."""
    server = subprocess.Popen([sys.executable, str(HIER / 'pages_server.py'), str(poort), str(map_)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        with socket.socket() as s:
            if s.connect_ex(('localhost', poort)) == 0:
                return server
        time.sleep(0.1)
    server.terminate()
    raise RuntimeError(f'server op poort {poort} start niet')
