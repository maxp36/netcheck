
import json

from pysnmp.hlapi import *
from pysnmp.proto.rfc1902 import *

import oids
import utils


class Node:
    def __init__(self, ip="", model="", sys_name="", sys_desc="", sys_cap_supported="", sys_cap_enabled="", loc_ports=None):
        self.ip = ip
        self.model = model
        self.sys_name = sys_name
        self.sys_desc = sys_desc
        self.sys_cap_supported = sys_cap_supported
        self.sys_cap_enabled = sys_cap_enabled
        self.loc_ports = {} if loc_ports is None else loc_ports
        # self.__chassisIdSubtype
        # self.__chassisId
        # self.__sysName = ""
        # self.__sysDesc = ""
        # self.__sysCapSupported = ""
        # self.__sysCapEnabled = ""

        # self.__manAddrLen = ""
        # self.__manAddrIfSubtype = ""
        # self.__manAddrIfId = ""
        # self.__manAddrOID = ""

        self.rem_ips = []
        # self.loc_ports = {}

        self.cap_bits = Bits.withNamedBits(repeater=1, bridge=2)

        # self.__ip = ".".join([str(x) for x in tuple(manAddrLen[0])[-4:]])

        # self.__get_info()

    # def getChassisIdSubtype(self):
    #     return self.chassis_id_subtype[1].prettyPrint()

    # def getChassisId(self):
    #     return self.chassis_id[1].prettyPrint()

    # def getSysName(self):
    #     return self.sys_name[1].prettyPrint()

    # def getSysDesc(self):
    #     return self.sys_desc[1].prettyPrint()

    # def getSysCapSupported(self):
    #     return self.cap_bits(self.sys_cap_supported[1]).prettyPrint()

    # def getSysCapEnabled(self):
    #     return self.cap_bits(self.sys_cap_enabled[1]).prettyPrint()

    # def getManAddrLen(self):
    #     return self.man_addr_len[1].prettyPrint()

    # def getManAddrIfSubtype(self):
    #     return self.__manAddrIfSubtype[1].prettyPrint()

    # def getManAddrIfId(self):
    #     return self.man_addr_if_id[1].prettyPrint()

    # def getManAddrOID(self):
    #     return "." + self.man_addr_oid[1].prettyPrint()

    # def getIP(self):
    #     return self.ip

    # def getRemIPs(self):
    #     return self.rem_ips

    # def getLocPorts(self):
    #     return self.loc_ports

    # def getModel(self):
    #     return self.model

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
        self.sys_name = vars[2][1].prettyPrint()
        self.sys_desc = vars[3][1].prettyPrint()
        self.sys_cap_supported = self.cap_bits(vars[4][1]).prettyPrint()
        self.sys_cap_enabled = self.cap_bits(vars[5][1]).prettyPrint()

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
                    0, 28,
                    ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpRemManAddrIfSubtype'])))

        oid = utils.get_snmp_var_binds(g)[0][0]
        while tuple(oid)[-10] == 3:
            loc_port = str(tuple(oid)[-8])
            rem_ip = ".".join([str(x) for x in tuple(oid)[-4:]])
            self.rem_ips.append(rem_ip)
            self.loc_ports[loc_port] = {}
            self.loc_ports[loc_port]["ip"] = rem_ip
            oid = utils.get_snmp_var_binds(g)[0][0]

        # получение описания и номера порта коммутатора-соседа на определенном локальном порту
        g = bulkCmd(engine,
                    CommunityData('unisnet'),
                    UdpTransportTarget((self.ip, 161)),
                    ContextData(),
                    0, 28,
                    ObjectType(ObjectIdentity(oids.local_system_data_oids['lldpRemPortDesc'])))

        vars = utils.get_snmp_var_binds(g)[0]
        oid, desc = vars[0], vars[1].prettyPrint()
        while tuple(oid)[-4] == 8:
            loc_port = str(tuple(oid)[-2])
            rem_port = desc.split('Port ')[1].split(' ')[0]
            self.loc_ports[loc_port]["remPortDesc"] = desc
            self.loc_ports[loc_port]["remPort"] = rem_port
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
              "lldpLocSysName : ", self.sys_name, "\n",
              "lldpLocSysDesc : ", self.sys_desc, "\n",
              "lldpLocSysCapSupported : ", self.sys_cap_supported, "\n",
              "lldpLocSysCapEnabled : ", self.sys_cap_enabled, "\n",
              "lldpLocManAddrLen : ", self.man_addr_len, "\n",
              "lldpLocManAddrIfSubtype : ", self.man_addr_if_subtype, "\n",
              "lldpLocManAddrIfId : ", self.man_addr_if_id, "\n",
              "lldpLocManAddrOID : ", self.man_addr_oid, "\n",
              "lldpRemManAddrs : ", self.rem_ips, "\n",
              "locPorts : ", json.dumps(self.loc_ports, sort_keys=True, indent=4), "\n")

    def print_min(self):
        print("[", self.ip, "]\n",
              "model : ", self.model, "\n",
              "lldpLocSysName : ", self.sys_name, "\n",
              "lldpLocSysDesc : ", self.sys_desc, "\n",
              "lldpLocSysCapSupported : ", self.sys_cap_supported, "\n",
              "lldpLocSysCapEnabled : ", self.sys_cap_enabled, "\n",
              "locPorts : ", json.dumps(self.loc_ports, sort_keys=True, indent=4), "\n")


def encode(node):
    return {
        "ip": node.ip,
        "model": node.model,
        "lldpLocSysName": node.sys_name,
        "lldpLocSysDesc": node.sys_desc,
        "lldpLocSysCapSupported": node.sys_cap_supported,
        "lldpLocSysCapEnabled": node.sys_cap_enabled,
        "locPorts": node.loc_ports
    }


def decode(node):
    if "locPorts" in node:
        return Node(node["ip"], node["model"], node["lldpLocSysName"], node["lldpLocSysDesc"], node["lldpLocSysCapSupported"], node["lldpLocSysCapEnabled"], node["locPorts"])
    return node
