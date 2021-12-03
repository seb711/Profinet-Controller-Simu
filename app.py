import random
import re
import sys
from flask import Flask, render_template, request
from turbo_flask import Turbo
import threading
import time
from scapy.all import *
from scapy.contrib.pnio import *
from messages.sim_pnio_ps import PNIOPSMessage

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


connection_dict = {
    "connection_state": "building....", 
    "connection": connection
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/build", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        result = request.form
        print(result["Name"])
        connection_dict["connection_state"] = "Building..."
        threading.Thread(
            target=build_connection,
            args=(result["Name"], result["IP"], result["IFace"], result["Path"]),
        ).start()
        return render_template("page2.html")


@app.route("/page2")
def page2():
    return render_template("page2.html")


@app.context_processor
def inject_load():
    return {
        "connection_state": connection_dict["connection_state"],
        "message_state": connection_dict["connection"].message_data.input_data,
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
            time.sleep(0.5)
            turbo.push(turbo.replace(render_template("loadavg.html"), "load"))


def main():
    print("test")


if __name__ == "__main__":
    main()
