import pymysql.cursors
import json
import utils

def get_info():
    conn = pymysql.connect(host='94.230.160.137',
                           user='nms_tplg',
                           password='choorohgae5Hiiy',
                           db='nms',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        # with conn.cursor() as cursor:
        #     # Create a new record
        #     sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
        #     cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

        # # connection is not autocommit by default. So you must commit to save
        # # your changes.
        # conn.commit()

        with conn.cursor() as cursor:
            # Read a single record
            # sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
            # cursor.execute(sql, ('webmaster@python.org',))
            sql = """
            select local_device.name as name, 
                local_device.descr as descr, 
                local_device.ip as loc_ip, 
                local_device.model as model,
                local_device.port as loc_port, 
                remote_device.ip as rem_ip,
                remote_device.port as rem_port

            from (select device.name as name, 
                        device.descr as descr, 
                        device.ip as ip,
                        device_model.name as model,
                        interface.index as port,
                        device_connection.link2_id as link
                from (((device
                        inner join interface on device.id = interface.device_id)
                        inner join device_model on device.device_model_id = device_model.id)
                        inner join device_connection on interface.id = device_connection.link1_id)) local_device,

                (select device.ip as ip,
                        interface.index as port,
                        device_connection.link2_id as link
                from (((device
                        inner join interface on device.id = interface.device_id)
                        inner join device_model on device.device_model_id = device_model.id)
                        inner join device_connection on interface.id = device_connection.link2_id)) remote_device

            where local_device.link = remote_device.link and local_device.ip = '172.16.0.1'

            union all

            select local_device.name as name, 
                local_device.descr as descr, 
                local_device.ip as loc_ip, 
                local_device.model as model,
                local_device.port as loc_port, 
                remote_device.ip as rem_ip,
                remote_device.port as rem_port

            from (select device.name as name, 
                        device.descr as descr, 
                        device.ip as ip,
                        device_model.name as model,
                        interface.index as port,
                        device_connection.link1_id as link
                from (((device
                        inner join interface on device.id = interface.device_id)
                        inner join device_model on device.device_model_id = device_model.id)
                        inner join device_connection on interface.id = device_connection.link2_id)) local_device,

                (select device.ip as ip,
                        interface.index as port,
                        device_connection.link1_id as link
                from (((device
                        inner join interface on device.id = interface.device_id)
                        inner join device_model on device.device_model_id = device_model.id)
                        inner join device_connection on interface.id = device_connection.link1_id)) remote_device

            where local_device.link = remote_device.link and local_device.ip = '172.16.0.1'

            order by loc_port;"""

            cursor.execute(sql)
            # result = cursor.fetchone()
            result = cursor.fetchall()

            dir_path = "./db_schema/"
            file_name = dir_path + "172.16.0.1.json"
            with utils.safe_open_w(file_name) as file:
                json.dump(result, file, indent=4)
            # print(json.dumps(result, sort_keys=True, indent=4))

            return result
    finally:
        conn.close()
