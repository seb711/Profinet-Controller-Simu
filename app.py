import random
import re
import sys
from flask import Flask, render_template, request, redirect
from turbo_flask import Turbo
import threading
import time
from scapy.all import *
from scapy.contrib.pnio import *
from messages.sim_pnio_ps import PNIOPSMessage
import json
from pnio_connection.connection import PNIOConnection

load_contrib("pnio")

app = Flask(__name__)
turbo = Turbo(app)

connection = PNIOConnection(
    device_name="name",
    device_ip="ip",
    iface="iface",
    path_to_gsdml="./gsdml/test_project_2.xml",
)
connection.message_data = PNIOPSMessage()

# connection.build_connection()


connection_dict = {"connection_state": "building....", "connection": connection}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/build", methods=["POST", "GET"])
def build():
    if request.method == "POST":
        result = request.form
        print(result["Name"])
        connection_dict["connection_state"] = "Building..."
        threading.Thread(
            target=build_connection,
            args=(result["Name"], result["IP"], result["IFace"], result["Path"]),
        ).start()
        return redirect(f"/page2")


@app.route("/sendValues", methods=["POST"])
def sendValues():
    # Validate the request body contains JSON
    data = json.loads(request.data)
    print(data)
    connection_dict["connection"].output_data = [
        a
        for a in connection_dict["connection"].output_data
        if not (
            data["module_ident"] == a["module_ident"]
            and data["submodule_ident"] == a["submodule_ident"]
        )
    ]

    print(connection_dict["connection"].output_data)

    connection_dict["connection"].output_data.append(data)

    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/page2")
def page2():
    output_data = []
    device = connection_dict["connection"].device
    usable_modules = device.body.dap_list[0].usable_modules
    for module in usable_modules:
        if module.used_in_slots != "" and module.output_length != 0:
            output_data.append({"module": module, "data_length": module.output_length})

    return render_template("page2.html", output_data=output_data)


@app.context_processor
def inject_load():
    return {
        "connection_state": connection_dict["connection_state"],
        "message_data": connection_dict["connection"].message_data.input_data,
        "message_info": connection_dict["connection"].message_data.data_status,
        "message_counter": connection_dict["connection"].message_data.cycle_counter,
    }


@app.before_first_request
def before_first_request():
    threading.Thread(target=update_data).start()


def build_connection(name, ip, iface, path):
    connection_dict["connection"] = PNIOConnection(
        device_name=name,
        device_ip=ip,
        iface=iface,
        path_to_gsdml=path,
    )
    connection_dict["connection"].build_connection()
    connection_dict["connection_state"] = "Application Ready!"


def update_data():
    with app.app_context():
        while True:
            time.sleep(0.1)
            turbo.push(turbo.replace(render_template("loadavg.html"), "load"))


def main():
    print("test")


if __name__ == "__main__":
    main()
