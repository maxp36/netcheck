import utils
import node


class NetworkComparator:
    def __init__(self, db):
        self.db = db

        self.nodes_ips = []
        self.state = {
            "differences": [],
            "matches": [],
            "not found": [],
            "not declared": []
        }

    def compare(self, ip):
        self.nodes_ips.append(ip)

        real = node.Node(ip)
        real.fetch()
        # self.nodes.append(n)

        decl = self.db.get_node(ip)
        decl = utils.combine_rows_to_one_node(decl)
        # decl = node.decode(decl)

        # print("real")
        # real.print()

        # print("decl")
        # decl.print()

        if real.is_empty() and not decl.is_empty():
            self.state["not found"].append(node.encode(decl))

        elif decl.is_empty() and not real.is_empty():
            self.state["not declared"].append(node.encode(real))

        else:
            comp = self.__compare_entities(real, decl)
            if "differences" in comp.keys():
                self.state["differences"].append(comp)
            else:
                self.state["matches"].append(comp["matches"])

        for i in real.rem_ips:
            if not (i in self.nodes_ips):
                self.compare(i)

        return self.state

    def __compare_entities(self, real, decl):
        if not isinstance(real, type(decl)):
            print("incomparable types", type(real), type(decl))

        if isinstance(real, str):
            return self.__compare_strs(real, decl)

        if isinstance(real, int):
            return self.__compare_ints(real, decl)

        if isinstance(real, dict):
            return self.__compare_dicts(real, decl)

        if isinstance(real, node.Node):
            return self.__compare_nodes(real, decl)

    def __compare_ints(self, real, decl):
        # print("compare ints:\n", "real\n", real, "decl\n", decl)
        if real == decl:
            return {"matches": real}
        else:
            return {"differences": {"real": real, "declared": decl}}

    def __compare_strs(self, real, decl):
        # print("compare string:\n", "real\n", real, "decl\n", decl)
        if real == decl:
            return {"matches": real}
        else:
            return {"differences": {"real": real, "declared": decl}}

    def __compare_nodes(self, real, decl):
        return self.__compare_entities(node.encode(real), node.encode(decl))

    def __compare_dicts(self, real, decl):

        # print("compare dicts:\n", "real\n", real, "\ndecl\n", decl)

        state = {}

        if len(real.keys()) == 0 and len(decl.keys()) == 0:
            state["matches"] = {}
            return state

        for key in decl.keys():

            if not (key in real.keys()):
                if not ("differences" in state.keys()):
                    state["differences"] = {}
                if not ("not found" in state["differences"].keys()):
                    state["differences"]["not found"] = {}
                state["differences"]["not found"][key] = decl[key]
                continue

            comp = self.__compare_entities(real[key], decl[key])

            # print("comp\n", comp)

            if "differences" in comp.keys():
                if not ("differences" in state.keys()):
                    state["differences"] = {}
                if not ("difference" in state["differences"].keys()):
                    state["differences"]["difference"] = {}
                state["differences"]["difference"][key] = comp
            # else:
            elif "matches" in comp.keys():
                if not ("matches" in state.keys()):
                    state["matches"] = {}
                state["matches"][key] = comp["matches"]

        for key in real.keys():
            if not (key in decl.keys()):
                if not ("differences" in state.keys()):
                    state["differences"] = {}
                if not ("not declared" in state["differences"].keys()):
                    state["differences"]["not declared"] = {}
                state["differences"]["not declared"][key] = real[key]

        return state
