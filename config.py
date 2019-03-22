import logging

import hjson


def check_config(config):
    logger = logging.getLogger(__name__)
    logger.info('netcheck configuration file check')
    check_config_db(config)
    check_config_hosts(config)
    check_config_aliases(config)
    check_config_limitations(config)


def check_config_db(config):
    logger = logging.getLogger(__name__)
    logger.info('db configuration check')
    config_err_text = 'config error:'
    if not 'db' in config:
        logger.error('%s "%s" field not defined' % (config_err_text, 'db'))
        exit(1)

    config_db = config['db']
    if not isinstance(config_db, dict):
        logger.error('%s "%s" field should be a dict' %
                     (config_err_text, 'db'))
        exit(1)

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
    if not isinstance(config_hosts, list):
        logger.error('%s "%s" field should be a list' %
                     (config_err_text, 'hosts'))
        exit(1)


def check_config_aliases(config):
    logger = logging.getLogger(__name__)
    logger.info('aliases configuration check')
    config_err_text = 'config error:'
    if not 'aliases' in config:
        config['aliases'] = {}

    config_aliases = config['aliases']
    if not isinstance(config_aliases, dict):
        logger.error('%s "%s" field should be a dict' %
                     (config_err_text, 'aliases'))
        exit(1)


def check_config_limitations(config):
    logger = logging.getLogger(__name__)
    logger.info('limitations configuration check')
    config_err_text = 'config error:'
    if not 'limitations' in config:
        config['limitations'] = {}

    config_limitations = config['limitations']
    if not isinstance(config_limitations, dict):
        logger.error('%s "%s" field should be a dict' %
                     (config_err_text, 'limitations'))
        exit(1)

    for key, config_limitation in config_limitations.items():
        check_config_limitation(config_limitation)
        config_limitations[key] = config_limitation

    config['limitations'] = config_limitations


def check_config_limitation(config):
    logger = logging.getLogger(__name__)
    config_err_text = 'limitations config error:'

    if not isinstance(config, dict):
        logger.error('%s "%s" value should be a dict' %
                     (config_err_text, 'limitation'))
        exit(1)

    if not 'check_ports' in config:
        config['check_ports'] = []
    if not 'exclude_ports' in config:
        config['exclude_ports'] = []

    if not isinstance(config['check_ports'], list):
        logger.error('%s "%s" field should be a list' %
                     (config_err_text, 'check_ports'))
        exit(1)

    if not isinstance(config['exclude_ports'], list):
        logger.error('%s "%s" field should be a list' %
                     (config_err_text, 'exclude_ports'))
        exit(1)
