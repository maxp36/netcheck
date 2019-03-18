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


def fetch_nodes_snmp(ip, limitations, nodes=[], nodes_ips=[]):
    n = node.Node(ip)
    n.fetch(limitations)
    if not n.is_empty():
        nodes.append(n)
    nodes_ips.append(ip)

    for i in n.rem_ips:
        if not (i in nodes_ips):
            nodes, nodes_ips = fetch_nodes_snmp(
                i, limitations, nodes, nodes_ips)

    return nodes, nodes_ips


def fetch_nodes_db(ip, node_db, limitations, nodes=[], nodes_ips=[]):
    limitation = utils.find_limitation_by_host(ip, limitations)

    n = node_db.get_node(ip)
    n = utils.combine_rows_to_one_node(n, limitation)
    if not n.is_empty():
        nodes.append(n)
    nodes_ips.append(ip)

    for i in n.rem_ips:
        if not (i in nodes_ips) and not i is None:
            nodes, nodes_ips = fetch_nodes_db(
                i, node_db, limitations, nodes, nodes_ips)

    return nodes, nodes_ips


def get_nodes_snmp(start_ip, limitations):
    logger = logging.getLogger(__name__)
    logger.info('getting switch information by LLDP')
    start = time.process_time()
    nodes, nodes_ips = fetch_nodes_snmp(start_ip, limitations)
    elapsed_time = round(time.process_time() - start, 3)
    logger.info('received information about %s switches by LLDP in %s seconds', len(
        nodes), elapsed_time)
    return nodes


def get_nodes_db(start_ip, db, limitations):
    logger = logging.getLogger(__name__)
    logger.info('getting switch information from database')
    start = time.process_time()
    nodes, nodes_ips = fetch_nodes_db(start_ip, db, limitations)
    elapsed_time = round(time.process_time() - start, 3)
    logger.info('received information about %s switches from database in %s seconds', len(
        nodes), elapsed_time)
    return nodes


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


def make_snapshot_snmp(start_ip, path, limitations):
    nodes = get_nodes_snmp(start_ip, limitations)
    utils.make_snapshot(path, nodes)


def make_snapshot_db(start_ip, path, db, limitations):
    nodes = get_nodes_db(start_ip, db, limitations)
    utils.make_snapshot(path, nodes)


def compare_real_and_declared(start_ip, path, db, limitations):
    real = get_nodes_snmp(start_ip, limitations)
    decl = get_nodes_db(start_ip, db, limitations)

    result = compare_networks(real, decl)
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

    with open(args.config, 'r') as f:
        cnf = hjson.load(f)

    with open(args.logconfig, 'r') as f:
        log_config = hjson.load(f)
        logging.config.dictConfig(log_config)

    logger = logging.getLogger(__name__)

    if args.operation is None:
        parser.print_help()
        exit(0)
        
    logger.info('start execution')

    if args.operation == 'store':
        if args.source == 'real':
            logger.info('"store real" command execution')
            config.check_config_hosts(cnf)

            hosts_cnf = cnf['hosts']
            host_cnf = hosts_cnf[0]
            ip = host_cnf['host']
            limitations = host_cnf['limitations']

            path = args.file

            make_snapshot_snmp(ip, path, limitations)

        elif args.source == 'declared':
            logger.info('"store declared" command execution')
            config.check_config(cnf)

            db_cnf = cnf['db']
            db_host = db_cnf['host']
            db_user = db_cnf['user']
            db_pass = db_cnf['pass']
            db_name = db_cnf['name']
            node_db = db.NodeDB(db_host, db_user, db_pass, db_name)

            hosts_cnf = cnf['hosts']
            host_cnf = hosts_cnf[0]
            ip = host_cnf['host']
            limitations = host_cnf['limitations']

            path = args.file

            make_snapshot_db(ip, path, node_db, limitations)

    elif args.operation == 'nms':
        logger.info('"nms" command execution')
        config.check_config(cnf)

        db_cnf = cnf['db']
        db_host = db_cnf['host']
        db_user = db_cnf['user']
        db_pass = db_cnf['pass']
        db_name = db_cnf['name']
        node_db = db.NodeDB(db_host, db_user, db_pass, db_name)

        hosts_cnf = cnf['hosts']
        host_cnf = hosts_cnf[0]
        ip = host_cnf['host']
        limitations = host_cnf['limitations']

        result_path = args.file

        compare_real_and_declared(ip, result_path, node_db, limitations)

    elif args.operation == 'cmp':
        logger.info('"cmp" command execution')
        real_path = args.real_file
        decl_path = args.decl_file
        result_path = args.result
        compare_from_files(real_path, decl_path, result_path)
