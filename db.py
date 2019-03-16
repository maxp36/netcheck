import json

import pymysql.cursors

import utils


class NodeDB:
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db

    def get_node(self, ip):
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

                where local_device.link = remote_device.link and local_device.ip = %s

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

                where local_device.link = remote_device.link and local_device.ip = %s 

                order by loc_port;"""

                cursor.execute(sql, (ip, ip,))
                result = cursor.fetchall()

                return result
        finally:
            conn.close()
