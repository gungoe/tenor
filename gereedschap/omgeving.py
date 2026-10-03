"""Gedeelde paden en hulpjes voor het gereedschap. De repo is de map boven deze."""
import pathlib, shutil, socket, subprocess, sys

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


def _poort_vrij(poort):
    """Vrij betekent: niemand luistert, op IPv4 noch IPv6, en wij kunnen hem nemen."""
    for familie, adres in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
        with socket.socket(familie) as s:
            s.settimeout(0.5)
            if s.connect_ex((adres, poort)) == 0:
                return False
    with socket.socket() as s:
        try:
            s.bind(('127.0.0.1', poort))
        except OSError:
            return False
    return True


def _vrije_poort():
    for _ in range(20):
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            poort = s.getsockname()[1]
        if _poort_vrij(poort):
            return poort
    raise RuntimeError('geen vrije poort gevonden')


def start_server(map_, poort):
    """Start pages_server.py (met Cache-Control: max-age=600, zoals GitHub Pages) en geeft het proces terug,
       met de poort waarop het luistert in .poort. Praat nooit met een server die het niet zelf startte:
       is de poort bezet, dan kiest het een vrije en meldt welke; en het wacht op het teken van zijn eigen
       proces, niet op een poort die toevallig antwoordt."""
    if not _poort_vrij(poort):
        vrij = _vrije_poort()
        print(f'poort {poort} is bezet (niet door dit gereedschap); de server draait op {vrij}')
        poort = vrij
    server = subprocess.Popen([sys.executable, str(HIER / 'pages_server.py'), str(poort), str(map_)],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    regel = server.stdout.readline().strip()          # pages_server meldt zich pas als hij zelf gebonden is
    if regel != f'luistert op {poort}':
        server.terminate()
        raise RuntimeError(f'server op poort {poort} start niet ({regel or "geen antwoord"})')
    server.poort = poort
    return server
