
import errno
import json
import os
import time

import node


def get_snmp_var_binds(g):
    error_indication, error_status, error_index, var_binds = next(g)

    if error_indication:  # SNMP engine errors
        print(error_indication)
    else:
        if error_status:  # SNMP agent errors
            print('%s at %s' % (error_status.prettyPrint(),
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


def make_snapshot(nodes, ip):
    current_time = time.strftime("%Y-%m-%d_%H-%M")
    dir_path = "./declared/"
    file_name = dir_path + ip + "_snapshot_" + current_time + ".json"
    with safe_open_w(file_name) as file:
        json.dump(nodes, file, default=node.encode,
                  sort_keys=True, indent=4)

    file_name = dir_path + "last_snapshot.json"
    with safe_open_w(file_name) as file:
        json.dump(nodes, file, default=node.encode,
                  sort_keys=True, indent=4)


def load_snapshot():
    dir_path = "./declared/"
    file_name = dir_path + "last_snapshot.json"
    with open(file_name) as file:
        return json.load(file, object_hook=node.decode)


def save_state(state):
    current_time = time.strftime("%Y-%m-%d_%H-%M")
    dir_path = "./real/"
    file_name = dir_path + "state_" + current_time + ".json"
    with safe_open_w(file_name) as file:
        json.dump(state, file, sort_keys=True, indent=4)




def find_by_ip(ip, nodes):
    for n in nodes:
        if n.ip == ip:
            return n
    return None


# def combine_arr_to_node_list(arr):
#     nodes = []

#     for row in arr:
#         loc_ip = row["loc_ip"]
#         loc_port = row["loc_port"]
#         rem_port = row["rem_port"]
#         rem_ip = row["rem_ip"]

#         n = find_by_ip(loc_ip, nodes)
#         if n is None:
#             model = row["model"]
#             name = row["name"]
#             ports = {}
#             ports[loc_port] = {
#                 "ip": rem_ip,
#                 "port": rem_port
#             }
#             n = node.Node(loc_ip, model, name, ports)
#             nodes.append(n)
#         else:
#             n.ports[loc_port] = {
#                 "ip": rem_ip,
#                 "port": rem_port
#             }

#     return nodes

def combine_rows_to_one_node(rows):
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

        n.ports[loc_port] = {
            "name": rem_name,
            "ip": rem_ip,
            "port": rem_port
        }

    return n
