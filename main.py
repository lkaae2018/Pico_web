import network
import socket
import time
from machine import Pin

WIFI_NAVN = "Pico-net"
WIFI_KODE = "12345678"

dioder = [
    Pin(0, Pin.OUT),
    Pin(1, Pin.OUT),
    Pin(2, Pin.OUT),
]

for diode in dioder:
    diode.value(0)


def lav_hjemmeside():
    html = """<!DOCTYPE html>
<html lang="da">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Pico – dioder</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin: 2em; }
        button { padding: 12px 20px; margin: 5px; font-size: 1em; }
    </style>
</head>
<body>
    <h1>Styr dioderne</h1>
"""
    for nummer, diode in enumerate(dioder, start=1):
        tilstand = "TÆNDT" if diode.value() else "SLUKKET"
        html += "<h2>Diode {}: {}</h2>".format(nummer, tilstand)
        html += '<a href="/{}/on"><button>Tænd</button></a>'.format(nummer)
        html += '<a href="/{}/off"><button>Sluk</button></a>'.format(nummer)

    html += "</body></html>"
    return html


ap = network.WLAN(network.AP_IF)
ap.config(essid=WIFI_NAVN, password=WIFI_KODE)
ap.active(True)

while not ap.active():
    time.sleep(0.1)

ip = ap.ifconfig()[0]
print("Wi-Fi-netværk:", WIFI_NAVN)
print("Adgangskode:", WIFI_KODE)
print("Åbn hjemmesiden på: http://" + ip)

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 80))
server.listen(2)

while True:
    klient, adresse = server.accept()
    try:
        forespoergsel = klient.recv(1024).decode()
        sti = forespoergsel.split(" ")[1]
        dele = sti.strip("/").split("/")

        if len(dele) == 2:
            try:
                nummer = int(dele[0])
                if 1 <= nummer <= len(dioder):
                    valgt_diode = dioder[nummer - 1]

                    if dele[1] == "on":
                        # Sluk alle dioder, og tænd derefter den valgte
                        for diode in dioder:
                            diode.value(0)
                        valgt_diode.value(1)

                    elif dele[1] == "off":
                        valgt_diode.value(0)
            except ValueError:
                pass

        side = lav_hjemmeside()
        svar = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "Connection: close\r\n\r\n"
            + side
        )
        klient.send(svar.encode())
    except Exception as fejl:
        print("Fejl:", fejl)
    finally:
        klient.close()