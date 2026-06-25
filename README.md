# Bjorn CyberViking – Home Assistant Integration (inoffiziell)

Diese Custom Integration holt sich von deinem Bjorn (dem netzwerkscannenden
e-Paper-Tamagotchi auf Raspberry-Pi-Basis von infinition) zwei Dinge nach
Home Assistant:

- **Sensoren** mit den wichtigsten Kennzahlen (Status, gefundene Ziele,
  Schwachstellen, geknackte Zugangsdaten, erbeutete Dateien, Zombie-Hosts)
- **Eine Kamera-Entity**, die laufend das aktuelle Bild des e-Paper-Displays
  zeigt – also genau die Stelle, an der die kleine Bjorn-Figur zu sehen ist.
  Auf dem Dashboard kannst du daraus z.B. eine "Picture Entity"-Karte bauen,
  die sich automatisch aktualisiert.

## ⚠️ Wichtiger Hinweis zur API

Bjorn selbst bietet **kein offiziell dokumentiertes JSON-API**. Diese
Integration geht davon aus, dass unter `http://<host>:<port>/status.json`
ein JSON mit Status-Infos liegt und unter `/screen.png` das aktuelle
Display-Bild. Das ist eine sinnvolle Annahme basierend auf der Code-Struktur
des Projekts (`shared.py`, `display.py`), aber **du solltest das vor der
Installation einmal selbst gegen deine laufende Instanz testen**:

```bash
curl http://<bjorn-ip>:8000/status.json
curl http://<bjorn-ip>:8000/screen.png --output test.png
```

Falls die Pfade bei dir anders heißen (z.B. weil du eine neuere/ältere
Bjorn-Version nutzt), passe einfach `STATUS_PATH` und `SCREEN_IMAGE_PATH`
in `const.py` an. Genauso können die JSON-Schlüssel in `sensor.py`
(`value_fn`) abweichen – schau dir dazu einfach die Ausgabe von
`curl .../status.json` an und passe die `.get("...")`-Aufrufe entsprechend an.

Falls dein Bjorn **gar kein** JSON-Status-Endpoint hat (sehr wahrscheinlich,
da das Projekt primär für das e-Paper-Display gebaut ist), bleibt dir die
Kamera-Entity trotzdem – die zeigt einfach `screen.png`, das von Bjorn
sowieso laufend aktualisiert wird, egal ob es einen Status-Endpoint gibt
oder nicht.

## Installation über HACS (als Custom Repository)

1. HACS muss bereits installiert sein.
2. In HACS: **Drei-Punkte-Menü → Benutzerdefinierte Repositories**
3. URL des Repos eintragen (z.B. dein eigenes GitHub-Repo, in das du diesen
   Ordner hochlädst), Kategorie: **Integration**
4. "Bjorn CyberViking" installieren
5. Home Assistant neu starten
6. **Einstellungen → Geräte & Dienste → Integration hinzufügen → "Bjorn CyberViking"**
   suchen, IP/Hostname und Port (Standard 8000) eingeben

## Manuelle Installation (ohne eigenes GitHub-Repo)

Einfach den Ordner `custom_components/bjorn_cyberviking` in dein
Home-Assistant-Konfigurationsverzeichnis kopieren (also nach
`/config/custom_components/bjorn_cyberviking`), dann HA neu starten und wie
oben ab Schritt 6 weitermachen.

## Dashboard-Karte (Beispiel)

```yaml
type: picture-entity
entity: camera.bjorn_cyberviking_bildschirm
camera_view: live
show_state: false
show_name: true
```

Für die Key-Werte z.B. eine einfache Entities- oder Glance-Karte mit den
erzeugten `sensor.*`-Entities.
