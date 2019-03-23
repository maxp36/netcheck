import node


class NetworkComparator:

    def compare(self, real, decl):
        state = {
            "found": {},
            "not found": {},
            "not declared": {}
        }

        for d in decl:
            r = self.__find_by_ip(d.ip, real)
            if r is None:
                state["not found"][d.ip] = node.encode(d)
                continue

            result = self.__compare_entities(r, d)
            state['found'][d.ip] = result

        for r in real:
            d = self.__find_by_ip(r.ip, decl)
            if d is None:
                state["not declared"][r.ip] = node.encode(r)

        return state

    def __compare_entities(self, real, decl):
        if not isinstance(real, type(decl)):
            print("incomparable types", type(real), type(decl))

        if isinstance(real, int) or isinstance(real, str):
            return self.__compare_primitive(real, decl)

        if isinstance(real, dict):
            return self.__compare_dicts(real, decl)

        if isinstance(real, node.Node):
            return self.__compare_nodes(real, decl)

    def __compare_primitive(self, real, decl):
        state = {
            'matches': {},
            'differences': {},
            'not found': {},
            'not declared': {}
        }
        if real == decl:
            state['matches'] = real
        else:
            state['differences']['real'] = real
            state['differences']['declared'] = decl

        return state

    def __compare_dicts(self, real, decl):
        state = {
            'matches': {},
            'differences': {},
            'not found': {},
            'not declared': {}
        }

        if len(real.keys()) == 0 and len(decl.keys()) == 0:
            return state

        for key in decl.keys():

            if not (key in real.keys()):
                state["not found"][key] = decl[key]
                continue

            result = self.__compare_entities(real[key], decl[key])
            for k, v in result.items():
                if v:
                    state[k][key] = v

        for key in real.keys():
            if not (key in decl.keys()):
                state["not declared"][key] = real[key]

        return state

    def __compare_nodes(self, real, decl):
        return self.__compare_entities(node.encode(real), node.encode(decl))

    def __find_by_ip(self, ip, nodes):
        for n in nodes:
            if n.ip == ip:
                return n
        return None
