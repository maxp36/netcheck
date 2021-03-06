import json
import logging

from pysnmp.hlapi import *
from pysnmp.proto.rfc1902 import *

import oids
import utils


class Node:
    def __init__(self, ip="", name="", ports=None):
        self.ip = ip
        self.name = name
        self.ports = {} if ports is None else ports

        self.rem_ips = []
        self.max_num_ports = 256

        self.logger = logging.getLogger(__name__)

    def fetch(self, community, aliases, limitation):
        self.logger.info('getting switch information (%s) by LLDP' % self.ip)
        engine = SnmpEngine()

        # получение локальных данных коммутатора
        g = getCmd(engine,
                   CommunityData(community),
                   UdpTransportTarget((self.ip, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpLocSysName'])))
        vals = utils.get_snmp_var_binds(g, self.ip)
        if len(vals) != 0:
            self.name = vals[0][1].prettyPrint()

        # получение IP коммутаторов-соседей и номеров локальных портов, к которым они подключенны
        g = bulkCmd(engine,
                    CommunityData(community),
                    UdpTransportTarget((self.ip, 161)),
                    ContextData(),
                    0, self.max_num_ports,
                    ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpRemManAddrIfSubtype'])))
        vals = utils.get_snmp_var_binds(g, self.ip)
        if len(vals) != 0:
            oid = vals[0][0]
            while tuple(oid)[-10] == 3:
                loc_port = int(tuple(oid)[-8])
                rem_ip = ".".join([str(x) for x in tuple(oid)[-4:]])

                # получение имени коммутатора-соседа на порту loc_port
                gen = getCmd(engine,
                             CommunityData(community),
                             UdpTransportTarget((rem_ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpLocSysName'])))
                vs = utils.get_snmp_var_binds(gen, self.ip)
                if len(vs) != 0:
                    rem_name = vs[0][1].prettyPrint()
                else:
                    continue

                # заменяем IP на оригинальный IP, если так описано конфигурацией aliases
                if rem_name in aliases.keys():
                    rem_ip = aliases[rem_name]

                # ограничиваем обход согласно конфигу
                if utils.is_checked_port(loc_port, limitation):
                    self.rem_ips.append(rem_ip)

                if not (loc_port in self.ports.keys()):
                    self.ports[loc_port] = {}
                self.ports[loc_port]["ip"] = rem_ip
                self.ports[loc_port]["name"] = rem_name
                vals = utils.get_snmp_var_binds(g, self.ip)
                if len(vals) != 0:
                    oid = vals[0][0]
                else:
                    break

        # получение описания и номера порта коммутатора-соседа на определенном локальном порту
        g = bulkCmd(engine,
                    CommunityData(community),
                    UdpTransportTarget((self.ip, 161)),
                    ContextData(),
                    0, self.max_num_ports,
                    ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpRemPortDesc'])))
        vals = utils.get_snmp_var_binds(g, self.ip)
        if len(vals) != 0:
            oid, desc = vals[0][0], vals[0][1].prettyPrint()
            while tuple(oid)[-4] == 8:
                loc_port = int(tuple(oid)[-2])
                rem_port = int(desc.split('Port ')[1].split(' ')[0])
                if not (loc_port in self.ports.keys()):
                    self.ports[loc_port] = {}
                self.ports[loc_port]["port"] = rem_port
                # self.ports[loc_port]["portDesc"] = desc

                vals = utils.get_snmp_var_binds(g, self.ip)
                if len(vals) != 0:
                    oid, desc = vals[0][0], vals[0][1].prettyPrint()
                else:
                    break

    def print(self):
        print("[", self.ip, "]\n",
              "name : ", self.name, "\n",
              "ports : ", json.dumps(self.ports, sort_keys=True, indent=4), "\n")

    def is_empty(self):
        if self.name == "" or len(self.ports.keys()) == 0:
            return True
        else:
            return False


def encode(node):
    return {
        "ip": node.ip,
        "name": node.name,
        "ports": node.ports
    }


def decode(node):
    if "ports" in node:
        return Node(node["ip"], node["name"], node["ports"])
    return node


def print_nodes(nodes):
    for n in nodes:
        n.print()
