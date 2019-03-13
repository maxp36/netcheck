import argparse
import json

import hjson
from pysnmp.hlapi import *

import compare
import db
import node
import oids
import utils

VERSION = 'v0.1.0'


def fetch_nodes_snmp(ip, nodes, nodes_ips, expose_name='.*'):
    n = node.Node(ip)
    n.fetch(expose_name)
    if not n.is_empty():
        nodes.append(n)
    nodes_ips.append(ip)

    for i in n.rem_ips:
        if not (i in nodes_ips):
            nodes, nodes_ips = fetch_nodes_snmp(
                i, nodes, nodes_ips, expose_name)

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


def make_snapshot_snmp(start_ip, path, expose_name='.*'):
    nodes = []
    nodes_ips = []

    nodes, nodes_ips = fetch_nodes_snmp(
        start_ip, nodes, nodes_ips, expose_name)
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
    nodes, nodes_ips = fetch_nodes_snmp(
        start_ip, real, nodes_ips, expose_name_snmp)
    utils.make_snapshot(real_path, nodes)

    decl = []
    nodes_ips = []
    nodes, nodes_ips = fetch_nodes_db(
        start_ip, decl, nodes_ips, db, expose_name_db)
    utils.make_snapshot(decl_path, nodes)

    nc = compare.NetworkComparator()
    result = nc.compare(real, decl)
    utils.make_snapshot(result_path, result)


def compare_from_files(path1, path2, result_path):
    nodes1 = utils.load_snapshot(path1)
    nodes2 = utils.load_snapshot(path2)

    nc = compare.NetworkComparator()
    result = nc.compare(nodes1, nodes2)
    utils.make_snapshot(result_path, result)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(VERSION))
    parser.add_argument(
        '-c', '--config', help='config file path (default: %(default)s)', default='./netcheck.hjson')

    subparsers = parser.add_subparsers(
        title='operations', help='valid operations', dest='operation')

    parser_store = subparsers.add_parser(
        'store', help='perform a real network scan and save the result to a file')
    parser_store.add_argument(
        'file', help='result file path (default: %(default)s)', nargs='?', default='./files/store/last.json')

    parser_nms = subparsers.add_parser(
        'nms', help='scan the real and documented network, compare the topologies and write the comparison result to a file')
    parser_nms.add_argument('file', help='result file path (default: %(default)s)',
                            nargs='?', default='./files/nms/last.json')

    parser_cmp = subparsers.add_parser(
        'cmp', help='compare the topologies described in the input files and save the result to a file')
    parser_cmp.add_argument('file1', help='input file1 path')
    parser_cmp.add_argument('file2', help='input file2 path')
    parser_cmp.add_argument('result', help='result file path (default: %(default)s)',
                            nargs='?', default='./files/cmp/last.json')

    # parser_cmp = subparsers.add_parser(
    #     'cmp', help='compare the topologies described in the input files and save the result to a file. If only 2 files are specified, the following two topologies are compared: 1) from the input file; 2) real network topology.')
    # parser_cmp.add_argument('file1', help='input file1 path')
    # parser_cmp.add_argument(
    #     'file2', help='input file2 path (if not specified, real topology is scanned)', nargs='?')
    # parser_cmp.add_argument('result', help='result file path')

    # parser.add_argument(
    #     '-a', '--ip', help='IP address of the switch from which data collection begins')

    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = hjson.load(f)

    if args.operation == 'store':
        ip = config['hosts'][0]['host']
        path = args.file
        expose_name_snmp = 'csw.*'
        make_snapshot_snmp(ip, path, expose_name_snmp)

    elif args.operation == 'nms':
        ip = config['hosts'][0]['host']

        real_path = './snapshots_snmp/snapshot.json'
        decl_path = './snapshots_db/snapshot.json'
        result_path = args.file

        db_cfg = config['db']
        db_host = db_cfg['host']
        db_user = db_cfg['user']
        db_pass = db_cfg['pass']
        db_name = db_cfg['name']
        node_db = db.NodeDB(db_host, db_user, db_pass, db_name)

        expose_name_snmp = 'csw.*'
        expose_name_db = 'csw%'

        compare_real_and_declared(
            ip, real_path, decl_path, result_path, node_db, expose_name_snmp, expose_name_db)

    elif args.operation == 'cmp':
        path1 = args.file1
        path2 = args.file2
        result_path = args.result
        compare_from_files(path1, path2, result_path)
