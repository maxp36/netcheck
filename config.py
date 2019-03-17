import logging

import hjson


def check_config(config):
    logger = logging.getLogger(__name__)
    logger.info('netcheck configuration file check')
    check_config_db(config)
    check_config_hosts(config)


def check_config_db(config):
    logger = logging.getLogger(__name__)
    logger.info('db configuration check')
    config_err_text = 'config error:'
    if not 'db' in config:
        logger.error('%s "%s" field not defined' % (config_err_text, 'db'))
        exit(1)

    config_db = config['db']
    config_err_text = 'db config error:'
    if not 'host' in config_db:
        logger.error('%s "%s" field not defined' % (config_err_text, 'host'))
        exit(1)
    if not 'user' in config_db:
        logger.error('%s "%s" field not defined' % (config_err_text, 'user'))
        exit(1)
    if not 'pass' in config_db:
        logger.error('%s "%s" field not defined' % (config_err_text, 'pass'))
        exit(1)
    if not 'name' in config_db:
        logger.error('%s "%s" field not defined' % (config_err_text, 'name'))
        exit(1)


def check_config_hosts(config):
    logger = logging.getLogger(__name__)
    logger.info('hosts configuration check')
    config_err_text = 'config error:'
    if not 'hosts' in config:
        logger.error('%s "%s" field not defined' % (config_err_text, 'hosts'))
        exit(1)

    config_hosts = config['hosts']
    for index, config_host in enumerate(config_hosts):
        check_config_host(config_host)
        config_hosts[index] = config_host

    config['hosts'] = config_hosts


def check_config_host(config):
    logger = logging.getLogger(__name__)
    config_err_text = 'hosts->host config error:'
    if not 'host' in config:
        logger.error('%s "%s" field not defined in\n %s' %
                     (config_err_text, 'host', hjson.dumps(config)))
        exit(1)
    if not 'limitations' in config:
        config['limitations'] = []
    else:
        config_limitations = config['limitations']
        for index, config_limitation in enumerate(config_limitations):
            check_config_limitation(config_limitation)
            config_limitations[index] = config_limitation

        config['limitations'] = config_limitations


def check_config_limitation(config):
    logger = logging.getLogger(__name__)
    config_err_text = 'hosts->host->restrict_nodes config error:'
    if not 'host' in config:
        logger.error('%s "%s" field not defined in\n %s' %
                     (config_err_text, 'host', hjson.dumps(config)))
        exit(1)
    if not 'aliases' in config:
        config['aliases'] = []
    if not 'check_ports' in config:
        config['check_ports'] = []
    if not 'exclude_ports' in config:
        config['exclude_ports'] = []
