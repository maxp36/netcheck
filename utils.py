
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


def make_snapshot(nodes):
    current_time = time.strftime("%Y-%m-%d_%H-%M")
    dir_path = "./declared/"
    file_name = dir_path + "snapshot_" + current_time + ".json"
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


def compare_networks(real, decl):
    state = {
        "differences": [],
        "matches": [],
        "not found": [],
        "not declared": []
    }

    for d in decl:
        r = find_by_ip(d.ip, real)
        if r is None:
            state["not found"].append(node.encode(d))
            continue

        comp = compare_entities(r, d)
        if "differences" in comp.keys():
            state["differences"].append(comp)
        else:
            state["matches"].append(comp["matches"])
        # state["not found"].append(comp["not found"])
        # state["not declared"].append(comp["not declared"])

    for r in real:
        d = find_by_ip(r.ip, decl)
        if d is None:
            state["not declared"].append(node.encode(r))

        # for k in comp.keys():

        #     if "differences" in comp.keys():
        #         if k == "differences":
        #             if not ("differences" in state.keys()):
        #                 state["differences"] = []
        #             state["differences"].append(comp)

        #     if "matches" in comp.keys():
        #         if k == "matches":
        #             if not ("matches" in state.keys()):
        #                 state["matches"] = []
        #             state["matches"].append(comp[k])

        #     if "not found" in comp.keys():
        #         if k == "not found":
        #             if not ("not found" in state.keys()):
        #                 state["not found"] = []
        #             state["not found"].append(comp[k])

        #     if "not declared" in comp.keys():
        #         if k == "not declared":
        #             if not ("not declared" in state.keys()):
        #                 state["not declared"] = []
        #             state["not declared"].append(comp[k])

            # if "differences" in comp.keys():
            #     if k == "differences":
            #         if not ("differences" in state.keys()):
            #             state["differences"] = []
            #         state["differences"].append(comp)
            # else:
            #     if k == "matches":
            #         if not ("matches" in state.keys()):
            #             state["matches"] = []
            #         state["matches"].append(comp[k])

    # for r in real:
    #     d = find_by_ip(r.ip, decl)
    #     if d is None:
    #         if not ("not declared" in state.keys()):
    #             state["not declared"] = []
    #         state["not declared"].append(node.encode(r))

    return state


def compare_entities(real, decl):
    if not isinstance(real, type(decl)):
        print("incomparable types", type(real), type(decl))

    if isinstance(real, str):
        return compare_strs(real, decl)

    if isinstance(real, dict):
        return compare_dicts(real, decl)

    if isinstance(real, node.Node):
        return compare_nodes(real, decl)


def compare_strs(real, decl):
    if real == decl:
        return {"matches": real}
    else:
        return {"differences": {"real": real, "declared": decl}}


def compare_dicts(real, decl):
    # if len(real.keys() - decl.keys()) != 0 or len(decl.keys() - real.keys()) != 0:
    #     print("incomparable dicts", real, decl)
    #     return None

    state = {}

    for key in decl.keys():

        if not (key in real.keys()):
            if not ("differences" in state.keys()):
                state["differences"] = {}
            if not ("not found" in state["differences"].keys()):
                state["differences"]["not found"] = {}
            state["differences"]["not found"][key] = decl[key]
            continue

        comp = compare_entities(real[key], decl[key])

        if "differences" in comp.keys():
            if not ("differences" in state.keys()):
                state["differences"] = {}
            if not ("difference" in state["differences"].keys()):
                state["differences"]["difference"] = {}
            state["differences"]["difference"][key] = comp
        else:
            if not ("matches" in state.keys()):
                state["matches"] = {}
            state["matches"][key] = comp["matches"]

        # if "not found" in comp.keys():
        #     if not ("not found" in state.keys()):
        #         state["not found"] = {}
        #     state["not found"][key] = comp["not found"]

        # if "not declared" in comp.keys():
        #     if not ("not declared" in state.keys()):
        #         state["not declared"] = {}
        #     state["not declared"][key] = comp["not declared"]

    for key in real.keys():
        if not (key in decl.keys()):
            if not ("differences" in state.keys()):
                state["differences"] = {}
            if not ("not declared" in state["differences"].keys()):
                state["differences"]["not declared"] = {}
            state["differences"]["not declared"][key] = real[key]

    # for key in real.keys():
    #     comp = compare_entities(real[key], decl[key])
    #     if "differences" in comp.keys():
    #         for k in comp.keys():
    #             if k == "differences":
    #                 if not ("differences" in ret.keys()):
    #                     ret["differences"] = {}
    #                 ret["differences"][key] = comp
    #     else:
    #         for k in comp.keys():
    #             if k == "matches":
    #                 if not ("matches" in ret.keys()):
    #                     ret["matches"] = {}
    #                 ret["matches"][key] = comp[k]

    # print(json.dumps(state, indent=4, sort_keys=True))
    return state


def compare_nodes(real, decl):
    return compare_entities(node.encode(real), node.encode(decl))


def find_by_ip(ip, nodes):
    for n in nodes:
        if n.ip == ip:
            return n
    return None


def combine_arr_to_node_list(arr):
    nodes = []

    for row in arr:
        loc_ip = row["loc_ip"]
        loc_port = row["loc_port"]
        rem_port = row["rem_port"]
        rem_ip = row["rem_ip"]

        n = find_by_ip(loc_ip, nodes)
        if n is None:
            model = row["model"]
            name = row["name"]
            descr = row["descr"]
            ports = {}
            ports[loc_port] = {
                "ip": rem_ip,
                "port": rem_port
            }
            n = node.Node(loc_ip, model, name, descr, ports)
            nodes.append(n)
        else:
            n.ports[loc_port] = {
                "ip": rem_ip,
                "port": rem_port
            }

    return nodes
