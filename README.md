# Mesh Master

Der Mesh Master für den Raspberry Pi welcher die Kommunikation über NRF24 ermöglicht. Hierfür wurde das [pyrf24](https://pypi.org/project/pyrf24/) package verwendet.

## Projekt Aufbau

### [main.py](https://github.com/my-mesh/mesh/blob/main/main.py)
```py
SERVER_URL = "http://127.0.0.1:5000/nodes"
```
Die Server URL wird definiert um die Decodeten Daten an den Webserver per Post Request zu senden.
<br><br>
```py
radio = RF24(22, 10)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)
```
Der NRF24 Chip wird gestartet und konfiguriert  
<br><br>

```py
while True:
    time.sleep(0.01)
    mesh.update()
    mesh.dhcp()
```
Solange das Programm läuft wird das Netzwerk geupdatet und das Dynamic Host Configuration Protocol(DHCP) am laufen gehalten
<br><br>

```py
while network.available():
    header, payload = network.read()
    node_id = mesh.get_node_id(header.from_node)
    network_id = header.from_node
    
    node = {"node_id": node_id, "network_id": network_id}
```
Empfagene Nachrichten werden zwischengespeichert und die NodeID sowie NetworkID wird gespeichert
<br><br>

Stellt das Hauptscript bereit. Zunächst wird der NRF24 Chip konfiguriert und das Mesh und Network gestartet. Daraufhin wird innerhalb der Schleife auf neue Funknachrichten gewartet. Falls welche empfangen werden, wird der empfangenen Payload decoded und an den Web-Server zum Speichern gesendet.

### [constant.py](https://github.com/my-mesh/mesh/blob/main/constant.py)
Stellt die Festgelegten Message Types für Master und Slave Nachrichten bereit. Ermöglicht das korrekte decoden eingehender Nachrichten sowie das Filtern von unbekannten Nachrichten

### [utils](https://github.com/my-mesh/mesh/tree/main/utils)
In diesem Ordner befinden sich einige Utility Funktionen.

### [.service](https://github.com/my-mesh/mesh/blob/main/.service)
Beispiel für eine systemd service Datei. Dadurch kann das Script automatisch beim Starten des Raspberry Pi gestartet werden.
