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

# Echte, im Bjorn-Quellcode (webapp.py) gefundene Endpunkte:
# - netkb_data_json liefert die komplette "Network Knowledge Base" als JSON
#   (eine Liste von Host-Datensätzen mit Alive-Status, Ports, Vulnerabilities, ...)
# - list_credentials liefert die Liste der geknackten Zugangsdaten
NETKB_PATH = "/netkb_data_json"
CREDENTIALS_PATH = "/list_credentials"

ATTR_ORCH_STATUS = "orchestrator_status"
ATTR_LAST_SEEN = "last_seen"
