import json, sys
bron, data, uit = sys.argv[1], sys.argv[2], sys.argv[3]
opties = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
s = open(bron).read()
d = open(data).read() if data != '-' else None
# alleen voor de voorbeeldweergave: de letters van Google, want letters/ is in deze omgeving leeg
s = s.replace('</head>', '<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">\n</head>', 1)
s = s.replace('<div class="app" id="app">', '<div class="app" id="app">\n  <div class="voorbeeld-label label">Voorbeeld · fictieve cijfers</div>')
if d is not None:
    s = s.replace('Schermen.opstarten();', f'Schermen.start({d}, {json.dumps({"nu": "2026-09-11T09:00:00+02:00", **opties})});')
open(uit, 'w').write(s)
