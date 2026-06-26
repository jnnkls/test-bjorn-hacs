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
Integration nutzt zwei tatsächlich im Bjorn-Quellcode (`webapp.py`)
vorhandene Endpunkte:

- `/netkb_data_json` – die "Network Knowledge Base" (alle Hosts mit
  Alive-Status, offenen Ports, Schwachstellen, ...)
- `/list_credentials` – Liste der geknackten Zugangsdaten
- `/screen.png` – das aktuelle Bild des e-Paper-Displays

Daraus werden die Sensor-Werte (gefundene Ziele, Schwachstellen,
Zugangsdaten, Zombies) selbst zusammengezählt. **Teste vor der Installation
einmal selbst**, ob diese Endpunkte bei dir antworten:

```bash
curl http://<bjorn-ip>:8000/netkb_data_json
curl http://<bjorn-ip>:8000/list_credentials
curl http://<bjorn-ip>:8000/screen.png --output test.png
```

Falls die Spaltennamen in der `netkb_data_json`-Antwort bei deiner
Bjorn-Version abweichen (z.B. weil sich das Datenmodell zwischenzeitlich
geändert hat), passe die Auswertung in `api.py`
(`_truthy_alive`, `_count_vulnerabilities`) entsprechend an.

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

## Update-Erkennung durch HACS

Damit HACS ein Update anzeigt, reicht das Hochsetzen der `version` in
`manifest.json` allein **nicht** – HACS orientiert sich an GitHub
**Releases/Tags** in deinem Repo, nicht direkt am Manifest-Inhalt. Wenn du
dieses Update in dein eigenes GitHub-Repo pushst, musst du zusätzlich einen
neuen Tag/Release anlegen, der zur Manifest-Version passt, z.B.:

```bash
git tag v0.2.0
git push origin v0.2.0
# und auf GitHub daraus ein Release erstellen
```

Erst dann sieht HACS bei den Nutzern ein verfügbares Update.

## Logo

`logo.png` (für die HACS-Übersicht) und `icon.png` (Integrations-Icon)
liegen im Repo-Root bzw. werden von HACS automatisch dort erwartet, wenn
`render_readme` aktiv ist. Beides ist ein selbst generiertes
Cyber-Wikinger-Logo (Helm + Schaltkreis-Motiv), kein Material aus dem
offiziellen Bjorn-Repo – dort gibt es kein freistehendes Logo-Asset, nur
Screenshots der e-Paper-Anzeige.
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
