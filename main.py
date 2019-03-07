import json
import argparse

from pysnmp.hlapi import *

import node
import oids
import utils
import db


def fetch_nodes(ip):
    n = node.Node(ip)
    n.fetch()
    nodes.append(n)
    nodes_ips.append(ip)

    for i in n.rem_ips:
        if not (i in nodes_ips):
            fetch_nodes(i)


nodes = []
nodes_ips = []

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--ip', help='IP address of the switch from which data collection begins')

    args = parser.parse_args()
    # print(args)

    fetch_nodes(args.ip)
    print(nodes_ips, "\n")

    utils.make_snapshot(nodes)

    # snapshot = utils.load_snapshot()
    # node.print_nodes_min(snapshot)
    # state = utils.compare_networks(nodes, snapshot)
    # utils.save_state(state)

    # node_rows = db.get_info()
    # node_list = utils.combine_arr_to_node_list(node_rows)

    # dir_path = "./db_schema/"
    # file_name = dir_path + "node_list.json"
    # with utils.safe_open_w(file_name) as file:
    #     json.dump(node_list, file, default=node.encode,
    #               sort_keys=True, indent=4)