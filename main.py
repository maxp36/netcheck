import json
import argparse

from pysnmp.hlapi import *

import node
import oids
import utils


def fetch_nodes(ip):
    n = node.Node(ip)
    n.fetch()
    nodes.append(n)
    nodes_ips.append(ip)

    for i in n.rem_ips:
        if not (i in nodes_ips):
            fetch_nodes(i)


def print_nodes(nodes):
    for n in nodes:
        n.print()


def print_nodes_min(nodes):
    for n in nodes:
        n.print_min()


nodes = []
nodes_ips = []

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--ip', help='IP address of the switch from which data collection begins')

    args = parser.parse_args()
    print(args)

    # get_nodes('172.16.250.253')
    fetch_nodes(args.ip)
    print(nodes_ips, "\n")
#     print_nodes_min(nodes)

    utils.make_snapshot(nodes)

    snapshot = utils.load_snapshot()
    print_nodes_min(snapshot)
    state = utils.compare_networks(nodes, snapshot)
    utils.save_state(state)
