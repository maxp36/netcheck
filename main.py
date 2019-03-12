import json
import argparse

from pysnmp.hlapi import *

import node
import oids
import utils
import db
import compare


def fetch_nodes_snmp(ip, nodes, nodes_ips, expose_name='.*'):
    n = node.Node(ip)
    n.fetch(expose_name)
    if not n.is_empty():
        nodes.append(n)
    nodes_ips.append(ip)

    for i in n.rem_ips:
        if not (i in nodes_ips):
            nodes, nodes_ips = fetch_nodes_snmp(i, nodes, nodes_ips, expose_name)

    return nodes, nodes_ips


def fetch_nodes_db(ip, nodes, nodes_ips, db, expose_name='%'):
    print('ip', ip)
    n = db.get_node(ip, expose_name)
    n = utils.combine_rows_to_one_node(n)
    if not n.is_empty():
        nodes.append(n)
    nodes_ips.append(ip)

    for i in n.rem_ips:
        if not (i in nodes_ips):
            nodes, nodes_ips = fetch_nodes_db(
                i, nodes, nodes_ips, db, expose_name)

    return nodes, nodes_ips


# nodes = []
# nodes_ips = []

def make_snapshot_snmp(start_ip, path, expose_name='.*'):
    nodes = []
    nodes_ips = []

    nodes, nodes_ips = fetch_nodes_snmp(start_ip, nodes, nodes_ips, expose_name)
    utils.make_snapshot(path, nodes)


def make_snapshot_db(start_ip, path, db, expose_name='%'):
    nodes = []
    nodes_ips = []

    nodes, nodes_ips = fetch_nodes_db(
        start_ip, nodes, nodes_ips, db, expose_name)
    utils.make_snapshot(path, nodes)


def compare_real_and_declared(start_ip, real_path, decl_path, result_path, db, expose_name_snmp='.*', expose_name_db='%'):
    real = []
    nodes_ips = []
    nodes, nodes_ips = fetch_nodes_snmp(start_ip, real, nodes_ips, expose_name_snmp)
    utils.make_snapshot(real_path, nodes)

    decl = []
    nodes_ips = []
    nodes, nodes_ips = fetch_nodes_db(
        start_ip, decl, nodes_ips, db, expose_name_db)
    utils.make_snapshot(decl_path, nodes)

    nc = compare.NetworkComparator()
    result = nc.compare(real, decl)
    utils.make_snapshot(result_path, result)


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

    # node_db = db.NodeDB('94.230.160.137', 'nms_tplg', 'choorohgae5Hiiy', 'nms')
    # node_rows = node_db.get_node(args.ip)
    # node_struct = utils.combine_rows_to_one_node(node_rows)

    # dir_path = "./db_schema/"
    # file_name = dir_path + args.ip + "_node.json"
    # with utils.safe_open_w(file_name) as file:
    #     json.dump(node_struct, file, default=node.encode,
    #               sort_keys=True, indent=4)

    # nc = compare.NetworkComparator(node_db)
    # comp = nc.compare(args.ip)

    # dir_path = "./comparisons/"
    # file_name = dir_path + args.ip + ".json"
    # with utils.safe_open_w(file_name) as file:
    #     json.dump(comp, file, sort_keys=True, indent=4)

#
    # make_snapshot_snmp(args.ip, './snapshots_snmp/snapshot.json')
#
    # node_db = db.NodeDB('94.230.160.137', 'nms_tplg', 'choorohgae5Hiiy', 'nms')
    # expose_name = "csw%"
    # make_snapshot_db(args.ip, './snapshots_db/snapshot.json', node_db, expose_name)
#
    real_path = './snapshots_snmp/snapshot.json'
    decl_path = './snapshots_db/snapshot.json'
    result_path = './snapshots_comparisons/snapshot.json'
    node_db = db.NodeDB('94.230.160.137', 'nms_tplg', 'choorohgae5Hiiy', 'nms')
    expose_name_snmp = 'csw.*'
    expose_name_db = 'csw%'
    compare_real_and_declared(
        args.ip, real_path, decl_path, result_path, node_db, expose_name_snmp, expose_name_db)
