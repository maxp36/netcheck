#!/usr/bin/python3
import argparse
import json
import logging
import logging.config
import time

import hjson

import compare
import config
import db
import node
import utils

VERSION = 'v0.1.0'


def fetch_nodes_snmp(ip, nodes, ips, aliases, limitations):
    if ip in ips:
        return nodes, ips

    limitation = None
    if ip in limitations.keys():
        limitation = limitations[ip]

    n = node.Node(ip)
    n.fetch(aliases, limitation)
    if not n.is_empty():
        nodes.append(n)
    ips.append(ip)

    for i in n.rem_ips:
        nodes, ips = fetch_nodes_snmp(
            i, nodes, ips, aliases, limitations)

    return nodes, ips


def fetch_nodes_db(ip, nodes, ips, node_db, limitations):
    if ip in ips:
        return nodes, ips

    limitation = None
    if ip in limitations.keys():
        limitation = limitations[ip]

    n = node_db.get_node(ip)
    n = utils.combine_rows_to_one_node(n, limitation)
    if not n.is_empty():
        nodes.append(n)
    ips.append(ip)

    for i in n.rem_ips:
        if not i is None:
            nodes, ips = fetch_nodes_db(
                i, nodes, ips, node_db, limitations)

    return nodes, ips


def get_nodes_snmp(start_ip, ips, aliases, limitations):
    logger = logging.getLogger(__name__)
    logger.info('getting switch information by LLDP')
    start = time.process_time()
    nodes = []
    nodes, ips = fetch_nodes_snmp(start_ip, nodes, ips, aliases, limitations)
    elapsed_time = round(time.process_time() - start, 3)
    logger.info('received information about %s switches by LLDP in %s seconds', len(
        nodes), elapsed_time)
    return nodes, ips


def get_nodes_db(start_ip, ips, db, limitations):
    logger = logging.getLogger(__name__)
    logger.info('getting switch information from database')
    start = time.process_time()
    nodes = []
    nodes, ips = fetch_nodes_db(start_ip, nodes, ips, db, limitations)
    elapsed_time = round(time.process_time() - start, 3)
    logger.info('received information about %s switches from database in %s seconds', len(
        nodes), elapsed_time)
    return nodes, ips


def compare_networks(real, decl):
    logger = logging.getLogger(__name__)
    logger.info('network comparison')
    nc = compare.NetworkComparator()
    start = time.process_time()
    result = nc.compare(real, decl)
    elapsed_time = round(time.process_time() - start, 3)

    is_diff = False
    if len(result['differences']) != 0 or len(result['not declared']) != 0 or len(result['not found']) != 0:
        is_diff = True
    logger.info(
        'comparison performed in %s seconds. Topologies are different: %s', elapsed_time, is_diff)

    return result


def make_snapshot_snmp(hosts, path, aliases, limitations):
    all = []
    ips = []
    for host in hosts:
        nodes, ips = get_nodes_snmp(host, ips, aliases, limitations)
        all.extend(nodes)
    utils.make_snapshot(path, all)


def make_snapshot_db(hosts, path, db, limitations):
    all = []
    ips = []
    for host in hosts:
        nodes, ips = get_nodes_db(host, ips, db, limitations)
        all.extend(nodes)
    utils.make_snapshot(path, all)


def compare_real_and_declared(hosts, path, db, aliases, limitations):
    all_real = []
    ips_real = []
    all_decl = []
    ips_decl = []
    for host in hosts:
        real, ips_real = get_nodes_snmp(host, ips_real, aliases, limitations)
        all_real.extend(real)
        decl, ips_decl = get_nodes_db(host, ips_decl, db, limitations)
        all_decl.extend(decl)

    result = compare_networks(all_real, all_decl)
    utils.make_snapshot(path, result)


def compare_from_files(real_path, decl_path, result_path):
    real = utils.load_snapshot(real_path)
    decl = utils.load_snapshot(decl_path)

    result = compare_networks(real, decl)
    utils.make_snapshot(result_path, result)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(VERSION))
    parser.add_argument(
        '-c', '--config', help='netcheck config file path (default: %(default)s)', default='./config/netcheck.hjson')
    parser.add_argument(
        '-lc', '--logconfig', help='log config file path (default: %(default)s)', default='./config/log.hjson')

    subparsers = parser.add_subparsers(
        title='operations', help='valid operations', dest='operation')

    parser_store = subparsers.add_parser(
        'store', help='perform a network scan and save the result to a file')
    parser_store_source = parser_store.add_subparsers(
        title='store operation', help='valid sources', dest='source')
    parser_store_source_real = parser_store_source.add_parser(
        'real', help='scan the real topology and save the result')
    parser_store_source_real.add_argument(
        'file', help='result file path (default: %(default)s)', nargs='?', default='./files/store/real/last.json')
    parser_store_source_declared = parser_store_source.add_parser(
        'declared', help='scan the declared topology and save the result')
    parser_store_source_declared.add_argument(
        'file', help='result file path (default: %(default)s)', nargs='?', default='./files/store/declared/last.json')

    parser_nms = subparsers.add_parser(
        'nms', help='scan the real and documented network, compare the topologies and write the comparison result to a file')
    parser_nms.add_argument('file', help='result file path (default: %(default)s)',
                            nargs='?', default='./files/nms/last.json')

    parser_cmp = subparsers.add_parser(
        'cmp', help='compare the topologies described in the input files and save the result to a file')
    parser_cmp.add_argument(
        'real_file', help='path to the file containing the real data')
    parser_cmp.add_argument(
        'decl_file', help='path to the file containing the declared data')
    parser_cmp.add_argument('result', help='result file path (default: %(default)s)',
                            nargs='?', default='./files/cmp/last.json')

    args = parser.parse_args()

    if args.operation is None:
        parser.print_help()
        exit(0)
    if args.source is None:
        parser_store.print_help()
        exit(0)

    with open(args.logconfig, 'r') as f:
        log_config = hjson.load(f)
        logging.config.dictConfig(log_config)

    logger = logging.getLogger(__name__)

    with open(args.config, 'r') as f:
        cnf = hjson.load(f)

    config.check_config(cnf)

    db_cnf = cnf['db']
    db_host = db_cnf['host']
    db_user = db_cnf['user']
    db_pass = db_cnf['pass']
    db_name = db_cnf['name']

    hosts = set(cnf['hosts'])
    aliases = cnf['aliases']
    limitations = cnf['limitations']

    logger.info('start execution')

    if args.operation == 'store':
        if args.source == 'real':
            logger.info('"store real" command execution')
            path = args.file
            make_snapshot_snmp(hosts, path, aliases, limitations)

        elif args.source == 'declared':
            logger.info('"store declared" command execution')
            node_db = db.NodeDB(db_host, db_user, db_pass, db_name)
            path = args.file
            make_snapshot_db(hosts, path, node_db, limitations)

    elif args.operation == 'nms':
        logger.info('"nms" command execution')
        node_db = db.NodeDB(db_host, db_user, db_pass, db_name)
        result_path = args.file
        compare_real_and_declared(
            hosts, result_path, node_db, aliases, limitations)

    elif args.operation == 'cmp':
        logger.info('"cmp" command execution')
        real_path = args.real_file
        decl_path = args.decl_file
        result_path = args.result
        compare_from_files(real_path, decl_path, result_path)
