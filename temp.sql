device.id device.name interface.id interface.device_id device_connection.link1_id device_connection.link2_id

CREATE TABLE `device_model` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(60) NOT NULL,
--     `descr` varchar(256) DEFAULT NULL,
--     `device_type_id` int(11) NOT NULL,
--     `has_ip` int(11) NOT NULL COMMENT '0 - device without ip, 1 - device 
--   with ip',
--     `manufacturer_id` int(11) NOT NULL,
--     `allow_net_virtual` int(11) NOT NULL DEFAULT '0',
--     `allow_misc_virtual` int(11) NOT NULL DEFAULT '0',
--     `allow_tel_virtual` int(11) NOT NULL DEFAULT '0',
    PRIMARY KEY (`id`),
    KEY `fk_device_model_device_type1` (`device_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8;

CREATE TABLE `device` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `name` varchar(60) NOT NULL,
      `descr` varchar(256) DEFAULT NULL,
      `ip` varchar(20) DEFAULT NULL,
      -- `ipv6` varchar(40) DEFAULT NULL,
      `device_model_id` int(11) NOT NULL,
      -- `location_id` int(11) DEFAULT NULL,
      -- `creator_id` int(11) NOT NULL,
      -- `creation_time` datetime NOT NULL,
      -- `editor_id` int(11) NOT NULL,
      -- `edit_time` datetime NOT NULL,
      -- `port` int(5) NOT NULL DEFAULT '0',
      -- `monitoring_enabled` int(11) NOT NULL COMMENT '0 - disabled, != 0 - enabled',
      -- `state` int(11) DEFAULT NULL COMMENT '0 - UNKNOWN, 1 - UP, 2 - DOWN',
      -- `serial_number` varchar(60) DEFAULT NULL,
      -- `product_number` varchar(60) DEFAULT NULL,
      -- `stock_number` varchar(60) DEFAULT NULL,
      -- `mon_current_status` int(11) DEFAULT NULL,
      -- `mon_type` varchar(16) DEFAULT NULL,
      -- `mon_params` varchar(254) DEFAULT NULL,
      -- `mon_time_avg` double DEFAULT NULL,
      -- `mon_time_best` double DEFAULT NULL,
      -- `mon_time_worst` double DEFAULT NULL,
      -- `mon_last_online` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      -- `mon_last_failed` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
      -- `mon_data` varchar(64) DEFAULT NULL,
      -- `mon_ping_count` int(11) DEFAULT NULL,
      -- `snmp_firmware_version` varchar(256) DEFAULT NULL,
      -- `snmp_hardware_version` varchar(256) DEFAULT NULL,
      -- `snmp_serial_number` varchar(256) DEFAULT NULL,
      -- `snmp_system_name` varchar(256) DEFAULT NULL,
      -- `snmp_system_location` varchar(256) DEFAULT NULL,
      -- `snmp_system_describe` varchar(256) DEFAULT NULL,
      -- `snmp_mac_address` binary(6) DEFAULT NULL,
      PRIMARY KEY (`id`),
      KEY `fk_device_device_model1` (`device_model_id`),
      KEY `device_idx` (`name`),
      KEY `location_id` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=526 DEFAULT CHARSET=utf8;

CREATE TABLE `interface` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `index` int(11) NOT NULL,
      -- `name` varchar(60) NOT NULL,
      -- `descr` text,
      -- `type_id` int(11) NOT NULL,
      `device_id` int(11) NOT NULL,
      `usage` int(11) NOT NULL,
      -- `property` varchar(60) DEFAULT '',
      -- `monitoring_enabled` int(11) NOT NULL COMMENT '0 - disabled, != 0 - enabled',
      -- `state` int(11) DEFAULT NULL COMMENT '0 - UNKNOWN, 1 - UP, 2 - DOWN  (for network interfaces only)',
      PRIMARY KEY (`id`),
      KEY `interface_idx` (`index`),
      KEY `device_id` (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15344 DEFAULT CHARSET=utf8;

CREATE TABLE `device_connection` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `link1_id` int(11) NOT NULL,
      `link2_id` int(11) NOT NULdevice
      -- `descr` varchar(60) DEFAULT NULL,
      PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1337 DEFAULT CHARSET=utf8;

device.name device.descr device.ip  interface.index  interface.index  device.name device.descr device.ip

select local_device.name as name, 
      local_device.descr as descr, 
      local_device.ip as loc_ip, 
      local_device.port as loc_port, 
      remote_device.ip as rem_ip,
      remote_device.port as rem_port

from (select device.name as name, 
            device.descr as descr, 
            device.ip as ip,
            interface.index as port,
            device_connection.link2_id as link
      from ((device
            inner join interface on device.id = interface.device_id)
            inner join device_connection on interface.id = device_connection.link1_id)) local_device,

      (select device.ip as ip,
            interface.index as port,
            device_connection.link2_id as link
      from ((device
            inner join interface on device.id = interface.device_id)
            inner join device_connection on interface.id = device_connection.link2_id)) remote_device

where local_device.link = remote_device.link and local_device.ip = '172.16.250.253';


-- from ((device
--       inner join interface on device.id = interface.device_id)
--       inner join device_connection on interface.id = device_connection.link1_id) as local_device,
--       ((device
--       inner join interface on device,id = interface.device_id)
--       inner join device_connection on interface.id = device_connection.link2_id) as remote_device


-- 
select * from (select device.name as name, 
            device.descr as descr, 
            device.ip as ip,
            interface.index as port,
            device_connection.link2_id as link
            from ((device
                  inner join interface on device.id = interface.device_id)
                  inner join device_connection on interface.id = device_connection.link1_id)) local_device

where local_device.ip = '172.16.250.253';


-- 

select device.name as name, 
            device.descr as descr, 
            device.ip as ip,
            interface.index as port,
            device_connection.link1_id,
            device_connection.link2_id
from ((device
      inner join interface on device.id = interface.device_id)
      inner join device_connection on interface.id = device_connection.link1_id)
where device.ip = '172.16.250.253';

-- 

select local_device.name as name, 
      local_device.descr as descr, 
      local_device.ip as loc_ip, 
      local_device.port as loc_port, 
      remote_device.ip as rem_ip,
      remote_device.port as rem_port

from (select device.name as name, 
            device.descr as descr, 
            device.ip as ip,
            interface.index as port,
            device_connection.link2_id as link
      from ((device
            inner join interface on device.id = interface.device_id)
            inner join device_connection on interface.id = device_connection.link1_id)) local_device,

      (select device.ip as ip,
            interface.index as port,
            device_connection.link2_id as link
      from ((device
            inner join interface on device.id = interface.device_id)
            inner join device_connection on interface.id = device_connection.link2_id)) remote_device

where local_device.link = remote_device.link
      and (local_device.ip = '172.16.250.253' or remote_device.ip = '172.16.250.253');


-- 

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

where local_device.link = remote_device.link and local_device.ip = '172.16.250.253'
order by name;

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

where local_device.link = remote_device.link and local_device.ip = '172.16.250.253'
order by name;

-- 

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

order by loc_port;


-- 
-- 
-- 

select local_device.name as loc_name, 
    --   local_device.descr as descr, 
      local_device.ip as loc_ip, 
      local_device.model as loc_model,
      local_device.port as loc_port, 
	  remote_device.name as rem_name, 
      remote_device.ip as rem_ip,
      remote_device.port as rem_port

from (select device.name as name, 
            -- device.descr as descr, 
            device.ip as ip,
            device_model.name as model,
            interface.index as port,
            device_connection.link2_id as link
      from (((device
            inner join interface on device.id = interface.device_id)
            inner join device_model on device.device_model_id = device_model.id)
            inner join device_connection on interface.id = device_connection.link1_id)) local_device,

      (select device.name as name,
	  		device.ip as ip,
            interface.index as port,
            device_connection.link2_id as link
      from (((device
            inner join interface on device.id = interface.device_id)
            inner join device_model on device.device_model_id = device_model.id)
            inner join device_connection on interface.id = device_connection.link2_id)) remote_device

where local_device.link = remote_device.link and local_device.ip = '172.16.0.1'

union all

select local_device.name as loc_name, 
    --   local_device.descr as descr, 
      local_device.ip as loc_ip, 
      local_device.model as loc_model,
      local_device.port as loc_port,
	  remote_device.name as rem_name, 
      remote_device.ip as rem_ip,
      remote_device.port as rem_port

from (select device.name as name, 
            -- device.descr as descr, 
            device.ip as ip,
            device_model.name as model,
            interface.index as port,
            device_connection.link1_id as link
      from (((device
            inner join interface on device.id = interface.device_id)
            inner join device_model on device.device_model_id = device_model.id)
            inner join device_connection on interface.id = device_connection.link2_id)) local_device,

      (select device.name as name,
	  		device.ip as ip,
            interface.index as port,
            device_connection.link1_id as link
      from (((device
            inner join interface on device.id = interface.device_id)
            inner join device_model on device.device_model_id = device_model.id)
            inner join device_connection on interface.id = device_connection.link1_id)) remote_device

where local_device.link = remote_device.link and local_device.ip = '172.16.0.1'

order by loc_port;