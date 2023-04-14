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

```py
index_network = get_index(new_nodes, network_id, "network_id")
index_node = get_index(new_nodes, node_id, "node_id")

if index_node != -1:
    new_nodes.pop(index_node)

if index_network != -1:
    mesh.write(
        struct.pack("i", new_nodes[index_network]["node_id"]), 90, 255
    )

if index_network == -1 and node_id == 255:
    try:
        req = requests.post(
            "http://127.0.0.1:5000/nodes", data={"type": header.type}
        )
        req_json = req.json()
        node["node_id"] = int(req_json["id"])
        new_nodes.append(node)
        mesh.write(struct.pack("i", int(req_json["id"])), 90, 255)
    except:
        print("Server not responding")
```
Falls eine Nachricht von NodeID 255 gesendet wurde. Handelt es sich hierbei um eine neue Node im System. Dementsprechend wird eine Post Request an den Webserver gesendet welcher eine neue Node in der Datenbank erstellt und eine freie ID welche nicht 255 ist zurücksendet. Diese ID wird jetzt an die Node mit der ID 255 gesendet bis diese die neue ID empfangen hat und geändert hat.
<br><br>

```py
payload_converted = convert_payload(payload, header.type)

result = dict()
result["payload"] = payload_converted
result["node_id"] = node_id
result["type"] = header.type

try:
    req = requests.post("http://127.0.0.1:5000/data", data=result)
except:
    print("Server not responding")
```
Der Payload (die Sensor Daten) werden decoded und anschließend an den Webserver gesendet welcher diese in der Datenbank speichert
<br><br>

### [constant.py](https://github.com/my-mesh/mesh/blob/main/constant.py)
Stellt die Festgelegten Message Types für Master und Slave Nachrichten bereit. Ermöglicht das korrekte decoden eingehender Nachrichten sowie das Filtern von unbekannten Nachrichten

### [utils](https://github.com/my-mesh/mesh/tree/main/utils)
In diesem Ordner befinden sich einige Utility Funktionen.

### [.service](https://github.com/my-mesh/mesh/blob/main/.service)
Beispiel für eine systemd service Datei. Dadurch kann das Script automatisch beim Starten des Raspberry Pi gestartet werden.
