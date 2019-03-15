import json

import pymysql.cursors

import utils


class NodeDB:
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db

    def get_node(self, ip, limitation):
        conn = pymysql.connect(host=self.host,
                               user=self.user,
                               password=self.password,
                               db=self.db,
                               cursorclass=pymysql.cursors.DictCursor)
        try:

            with conn.cursor() as cursor:
                sql = """
                select local_device.name as loc_name,  
                    local_device.ip as loc_ip, 
                    local_device.port as loc_port, 
                    remote_device.name as rem_name, 
                    remote_device.ip as rem_ip,
                    remote_device.port as rem_port

                from (select device.name as name, 
                            device.ip as ip,
                            interface.index as port,
                            device_connection.link2_id as link
                    from ((device
                            inner join interface on device.id = interface.device_id)
                            inner join device_connection on interface.id = device_connection.link1_id)) local_device,

                    (select device.name as name,
                        device.ip as ip,
                            interface.index as port,
                            device_connection.link2_id as link
                    from ((device
                            inner join interface on device.id = interface.device_id)
                            inner join device_connection on interface.id = device_connection.link2_id)) remote_device

                where local_device.link = remote_device.link and local_device.ip = '%s' and local_device.port %s  

                union all

                select local_device.name as loc_name, 
                    local_device.ip as loc_ip, 
                    local_device.port as loc_port,
                    remote_device.name as rem_name, 
                    remote_device.ip as rem_ip,
                    remote_device.port as rem_port

                from (select device.name as name, 
                            device.ip as ip,
                            interface.index as port,
                            device_connection.link1_id as link
                    from ((device
                            inner join interface on device.id = interface.device_id)
                            inner join device_connection on interface.id = device_connection.link2_id)) local_device,

                    (select device.name as name,
                        device.ip as ip,
                            interface.index as port,
                            device_connection.link1_id as link
                    from ((device
                            inner join interface on device.id = interface.device_id)
                            inner join device_connection on interface.id = device_connection.link1_id)) remote_device

                where local_device.link = remote_device.link and local_device.ip = '%s' and local_device.port %s  

                order by loc_port;"""

                where_port = ''
                if limitation is None:
                    where_port = "like '%'"
                else:
                    check_ports = limitation['check_ports']
                    exclude_ports = limitation['exclude_ports']
                    if len(check_ports) == 0 and len(exclude_ports) == 0:
                        where_port = "like '%'"
                    elif len(check_ports) == 0 and len(exclude_ports) != 0:
                        ports = '(%s)' % ', '.join(
                            [str(i) for i in exclude_ports])
                        where_port = "not in %s" % (ports)
                    elif len(check_ports) != 0 and len(exclude_ports) == 0:
                        ports = '(%s)' % ', '.join(
                            [str(i) for i in check_ports])
                        where_port = "in %s" % (ports)
                    elif len(check_ports) != 0 and len(exclude_ports) != 0:
                        dif = set(check_ports)-set(exclude_ports)
                        ports = '(%s)' % ', '.join([str(i) for i in dif])
                        where_port = "in %s" % (ports)
                sql = sql % (ip, where_port, ip, where_port)
                cursor.execute(sql)
                result = cursor.fetchall()

                # dir_path = "./db_schema/"
                # file_name = dir_path + ip + ".json"
                # with utils.safe_open_w(file_name) as file:
                #     json.dump(result, file, indent=4)

                return result
        finally:
            conn.close()
