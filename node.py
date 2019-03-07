
import json

from pysnmp.hlapi import *
from pysnmp.proto.rfc1902 import *

import oids
import utils


class Node:
    def __init__(self,
        ip="", 
        model="", 
        name="", 
        desc="", 
        # cap_supported="", 
        # cap_enabled="", 
        ports=None):
        self.ip = ip
        self.model = model
        self.name = name
        self.desc = desc
        # self.cap_supported = cap_supported
        # self.cap_enabled = cap_enabled
        self.ports = {} if ports is None else ports

        self.rem_ips = []

        self.cap_bits = Bits.withNamedBits(repeater=1, bridge=2)

        self.max_num_ports = 50

    def fetch(self):
        engine = SnmpEngine()

        # получение локальных данных коммутатора
        g = getCmd(engine,
                   CommunityData('unisnet'),
                   UdpTransportTarget((self.ip, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(
                       oids.local_system_data_oids['lldpLocChassisIdSubtype'])),
                   ObjectType(ObjectIdentity(
                       oids.local_system_data_oids['lldpLocChassisId'])),
                   ObjectType(ObjectIdentity(
                       oids.local_system_data_oids['lldpLocSysName'])),
                   ObjectType(ObjectIdentity(
                       oids.local_system_data_oids['lldpLocSysDesc'])),
                   ObjectType(ObjectIdentity(
                       oids.local_system_data_oids['lldpLocSysCapSupported'])),
                   ObjectType(ObjectIdentity(
                       oids.local_system_data_oids['lldpLocSysCapEnabled'])))

        vars = utils.get_snmp_var_binds(g)
        self.chassis_id_subtype = vars[0][1].prettyPrint()
        self.chassis_id = vars[1][1].prettyPrint()
        self.name = vars[2][1].prettyPrint()
        self.desc = vars[3][1].prettyPrint()
        # self.cap_supported = self.cap_bits(vars[4][1]).prettyPrint()
        # self.cap_enabled = self.cap_bits(vars[5][1]).prettyPrint()

        # получение данных о локальном адресе управления
        g = nextCmd(engine,
                    CommunityData('unisnet'),
                    UdpTransportTarget((self.ip, 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpLocManAddrLen'])))

        self.man_addr_len = utils.get_snmp_var_binds(g)[0][1].prettyPrint()
        self.man_addr_if_subtype = utils.get_snmp_var_binds(g)[
            0][1].prettyPrint()
        self.man_addr_if_id = utils.get_snmp_var_binds(g)[0][1].prettyPrint()
        self.man_addr_oid = utils.get_snmp_var_binds(g)[0][1].prettyPrint()

        # получение IP коммутаторов-соседей и номеров локальных портов, к которым они подключенны
        g = bulkCmd(engine,
                    CommunityData('unisnet'),
                    UdpTransportTarget((self.ip, 161)),
                    ContextData(),
                    0, self.max_num_ports,
                    ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpRemManAddrIfSubtype'])))

        oid = utils.get_snmp_var_binds(g)[0][0]
        while tuple(oid)[-10] == 3:
            loc_port = str(tuple(oid)[-8])
            rem_ip = ".".join([str(x) for x in tuple(oid)[-4:]])
            self.rem_ips.append(rem_ip)
            self.ports[loc_port] = {}
            self.ports[loc_port]["ip"] = rem_ip
            oid = utils.get_snmp_var_binds(g)[0][0]

        # получение описания и номера порта коммутатора-соседа на определенном локальном порту
        g = bulkCmd(engine,
                    CommunityData('unisnet'),
                    UdpTransportTarget((self.ip, 161)),
                    ContextData(),
                    0, self.max_num_ports,
                    ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpRemPortDesc'])))

        vars = utils.get_snmp_var_binds(g)[0]
        oid, desc = vars[0], vars[1].prettyPrint()
        while tuple(oid)[-4] == 8:
            loc_port = str(tuple(oid)[-2])
            rem_port = desc.split('Port ')[1].split(' ')[0]
            # self.ports[loc_port]["portDesc"] = desc
            self.ports[loc_port]["port"] = rem_port
            vars = utils.get_snmp_var_binds(g)[0]
            oid, desc = vars[0], vars[1].prettyPrint()

        # получение модели коммутатора
        g = nextCmd(engine,
                    CommunityData('unisnet'),
                    UdpTransportTarget((self.ip, 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpLocPortDesc'])))

        self.model = utils.get_snmp_var_binds(
            g)[0][1].prettyPrint().split('Port')[0]

    def print(self):
        print("[", self.ip, "]\n",
              "model : ", self.model, "\n",
              "lldpLocChassisIdSubtype : ", self.chassis_id_subtype, "\n",
              "lldpLocChassisId : ", self.chassis_id, "\n",
              "lldpLocSysName : ", self.name, "\n",
              "lldpLocSysDesc : ", self.desc, "\n",
            #   "lldpLocSysCapSupported : ", self.cap_supported, "\n",
            #   "lldpLocSysCapEnabled : ", self.cap_enabled, "\n",
              "lldpLocManAddrLen : ", self.man_addr_len, "\n",
              "lldpLocManAddrIfSubtype : ", self.man_addr_if_subtype, "\n",
              "lldpLocManAddrIfId : ", self.man_addr_if_id, "\n",
              "lldpLocManAddrOID : ", self.man_addr_oid, "\n",
              "lldpRemManAddrs : ", self.rem_ips, "\n",
              "locPorts : ", json.dumps(self.ports, sort_keys=True, indent=4), "\n")

    def print_min(self):
        print("[", self.ip, "]\n",
              "model : ", self.model, "\n",
              "name : ", self.name, "\n",
              "desc : ", self.desc, "\n",
            #   "capSupported : ", self.cap_supported, "\n",
            #   "capEnabled : ", self.cap_enabled, "\n",
              "ports : ", json.dumps(self.ports, sort_keys=True, indent=4), "\n")


def encode(node):
    return {
        "ip": node.ip,
        "model": node.model,
        "name": node.name,
        "desc": node.desc,
        "ports": node.ports
    }


def decode(node):
    if "ports" in node:
        return Node(node["ip"], node["model"], node["name"], node["desc"], node["ports"])
    return node


def print_nodes(nodes):
    for n in nodes:
        n.print()


def print_nodes_min(nodes):
    for n in nodes:
        n.print_min()
