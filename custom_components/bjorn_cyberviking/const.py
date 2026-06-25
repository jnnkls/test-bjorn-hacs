"""Constants for the Bjorn CyberViking integration."""

DOMAIN = "bjorn_cyberviking"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_PORT = 8000
DEFAULT_SCAN_INTERVAL = 10  # Sekunden - Bjorn rendert das e-Paper Bild relativ häufig neu

# Pfad zum aktuellen "Bildschirmfoto" des e-Paper-Displays.
# Bjorn schreibt dieses Bild laufend neu (siehe display.py / utils.py im Bjorn-Repo).
SCREEN_IMAGE_PATH = "/screen.png"

# Pfad zur Live-Status-Datei. ACHTUNG: Dieser Endpoint ist nicht offiziell
# dokumentiert. Bjorn schreibt lokal eine "livestatusfile" (siehe shared.py).
# Falls dein Bjorn diese nicht per HTTP unter diesem Pfad bereitstellt, musst
# du den Pfad in api.py anpassen (z.B. auf einen eigenen kleinen Export, den
# du selbst per cronjob/inotify auf den Webserver legst).
STATUS_PATH = "/status.json"

ATTR_ORCH_STATUS = "orchestrator_status"
ATTR_LAST_SEEN = "last_seen"
