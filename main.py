import json
import argparse

from pysnmp.hlapi import *

import node
import oids
import utils
import db
import compare


# def fetch_nodes(ip):
#     n = node.Node(ip)
#     n.fetch()
#     nodes.append(n)
#     nodes_ips.append(ip)

#     for i in n.rem_ips:
#         if not (i in nodes_ips):
#             fetch_nodes(i)


# nodes = []
# nodes_ips = []

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--ip', help='IP address of the switch from which data collection begins')

    args = parser.parse_args()
    # print(args)

    # fetch_nodes(args.ip)
    # print(nodes_ips, "\n")

    # utils.make_snapshot(nodes, args.ip)

    # snapshot = utils.load_snapshot()
    # node.print_nodes_min(snapshot)
    # state = utils.compare_networks(nodes, snapshot)
    # utils.save_state(state)

    node_db = db.NodeDB('94.230.160.137', 'nms_tplg', 'choorohgae5Hiiy', 'nms')
    # node_rows = node_db.get_node(args.ip)
    # node_struct = utils.combine_rows_to_one_node(node_rows)

    # dir_path = "./db_schema/"
    # file_name = dir_path + args.ip + "_node.json"
    # with utils.safe_open_w(file_name) as file:
    #     json.dump(node_struct, file, default=node.encode,
    #               sort_keys=True, indent=4)

    nc = compare.NetworkComparator(node_db)
    comp = nc.compare(args.ip)

    dir_path = "./comparisons/"
    file_name = dir_path + args.ip + ".json"
    with utils.safe_open_w(file_name) as file:
        json.dump(comp, file, sort_keys=True, indent=4)