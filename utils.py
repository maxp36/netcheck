import errno
import json
import logging
import os

import node


def get_snmp_var_binds(g, ip):
    logger = logging.getLogger(__name__)
    error_indication, error_status, error_index, var_binds = next(g)

    if error_indication:  # SNMP engine errors
        logger.error('ip: %s; error: %s' % (ip, error_indication))
    else:
        if error_status:  # SNMP agent errors
            logger.error('ip: %s; error: %s at %s' % (ip, error_status.prettyPrint(),
                                       var_binds[int(error_index)-1] if error_index else '?'))
        else:
            return var_binds
    return []


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def safe_open_w(path):
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')


def write_file_json(path, data, func=None):
    with safe_open_w(path) as file:
        json.dump(data, file, default=func, sort_keys=True, indent=4)


def read_file_json(path, func=None):
    with open(path) as file:
        return json.load(file, object_hook=func)


def make_snapshot(path,  data):
    write_file_json(path, data, node.encode)


def load_snapshot(path):
    return read_file_json(path, node.decode)


def combine_rows_to_one_node(rows, limitation):
    n = node.Node()
    if len(rows) == 0:
        return n

    row = rows[0]
    n.ip = row["loc_ip"]
    n.name = row["loc_name"]

    for row in rows:
        loc_port = row["loc_port"]
        rem_name = row["rem_name"]
        rem_port = row["rem_port"]
        rem_ip = row["rem_ip"]

        # ограничиваем обход согласно конфигу
        if is_checked_port(loc_port, limitation):
            n.rem_ips.append(rem_ip)

        n.ports[loc_port] = {
            "name": rem_name,
            "ip": rem_ip,
            "port": rem_port
        }

    return n


def is_checked_port(port, limitation):
    if limitation is None:
        return True
    else:
        check_ports = limitation['check_ports']
        exclude_ports = limitation['exclude_ports']
        if len(check_ports) == 0 and len(exclude_ports) == 0:
            return True
        elif len(check_ports) == 0 and len(exclude_ports) != 0:
            return not port in exclude_ports
        elif len(check_ports) != 0 and len(exclude_ports) == 0:
            return port in check_ports
        elif len(check_ports) != 0 and len(exclude_ports) != 0:
            return port in check_ports and not port in exclude_ports

def decode_limitation_ports(input):
    # 1 2(space)
    # 3-6
    # 7

    input = input.split()        
    # ["1 2 ", "3-6", "7"]

    tmp = []
    for s in input:
        t = s.strip().split()
        tmp.extend(t)
    # ["1", "2", "3-6", "7"]

    ret = []
    for s in tmp:
        p = s.split('-')
        if len(p) == 1 :
            ret.append(int(p[0]))
        elif len(p) == 2 :
            arr = fill_interval(int(p[0]), int(p[1]))
            ret.extend(arr)
    # [1, 2, 3, 4, 5, 6, 7]

    return ret

def fill_interval(start, end):
    ret = []
    if start > end :
        start, end = end, start
    while start <= end:
        ret.append(start)
        start += 1

    return ret