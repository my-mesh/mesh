import struct
import requests
import time
from pyrf24 import RF24, RF24Network, RF24Mesh
from utils.payload import convert_payload
from utils.index import get_index

SERVER_URL = "http://127.0.0.1:5000/nodes"

# RF24 Setup
radio = RF24(22, 10)
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)

# Master Node is always 0
mesh.node_id = 0

new_nodes = []

if not mesh.begin():
    raise OSError("Radio hardware not responding.")

print("Mesh started")

try:
    while True:
        time.sleep(0.01)
        mesh.update()
        mesh.dhcp()

        while network.available():
            header, payload = network.read()
            node_id = mesh.get_node_id(header.from_node)
            network_id = header.from_node

            print(node_id)
            print(network_id)

            node = {"node_id": node_id, "network_id": network_id}
            
            index_network = get_index(new_nodes, network_id, "network_id")
            index_node = get_index(new_nodes, node_id, "node_id")
            
            if index_node != -1:
                print("pop")
                new_nodes.pop(index_node)

            if index_network != -1:
                print("send_again")
                mesh.write(
                    struct.pack("i", new_nodes[index_network]["node_id"]), 90, 255
                )

            if index_network == -1 and node_id == 255:
                print("create new")
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

            payload_converted = convert_payload(payload, header.type)

            result = dict()
            result["payload"] = payload_converted
            result["node_id"] = node_id
            result["type"] = header.type

            print(result)

            try:
                req = requests.post("http://127.0.0.1:5000/data", data=result)
            except:
                print("Server not responding")
except:
    print("Mesh stopped")
    radio.power = False
