# netcheck
Comand-line utility to scan the network topology and find differences with a documented network structure


## netcheck config
### Basic config example
Сonfiguration file is in [HJSON](https://hjson.org/) format and by default has a path `./config/netcheck.hjson`

```hjson
{
    db: {
        host: host
        user: user
        pass: pass
        name: name
    }

    hosts: [
        {
            host: host
            limitations: [
                {
                    host: host
                    aliases: [
                        alias1
                        alias2
                    ]
                    check_ports: [port1, port2]
                    exclude_ports: [port3]
                }
            ]
        }
    ]
}
```

### Configuration file description
The configuration file contains two objects at the top level:

1. `db` - an object containing information about connecting to the database containing information about switches
    1. `host` - address to connect to the database (required)
    2. `user` - db login username (required)
    3. `pass` - db login password (required)
    4. `name` - database name (required)

2. `hosts` - array of `host` objects describing network scanning parameters

Each `host` object contains the following fields:

1. `host` - address of the switch that starts the network scan (required)
2. `limitations` - an array of objects describing additional scanning limitations

Each `limitation` object contains the following fields:

1. `host` - address of the switch to which the limitations apply (required)
2. `aliases` - an array of additional addresses that this switch can have
3. `check_ports` - an array of port numbers from which you want to continue scanning neighbor switches
4. `exclude_ports` - an array of port numbers from which scanning of neighbor switches should not continue

The following cases are possible:

1. `check_ports` is empty and `exclude_ports` is empty:
    
    Scan all possible neighbors on all ports.

    If the switch has neighbors on ports [1, 2, 3], all neighbors will be scanned.

2. `check_ports` is not empty and `exclude_ports` is empty:

    Scan neighbors on `check_ports` only

    If the switch has neighbors on ports [1, 2, 3], but `check_ports` is [1, 2], then only neighbors on ports [1, 2] will be scanned.

3. `check_ports` is empty and `exclude_ports` is not empty:

    Scan all possible neighbors except those located on `exclude_ports`

    If the switch has neighbors on ports [1, 2, 3], but `exclude_ports` is [1], then only neighbors on ports [2, 3] will be scanned.

4. `check_ports` is not empty and `exclude_ports` is not empty:

    Scan all possible neighbors that are on `check_ports` and not on `exclude_ports`

    If the switch has neighbors on ports [1, 2, 3, 4, 5], but `check_ports` is [1, 2, 3] and `exclude_ports` is [1], then only neighbors on ports [2, 3] will be scanned.


## Compare result file structure
### Result structure
The structure of nesting fields in the result file is shown below.

A field enclosed in square brackets (`[field]`) means that it may not be present in the result structure.
```
differences
    [diff...]
        differences
            [difference]
                key...
                    differences
                        [difference]
                            key...
                                differences
                                    [difference]
                                        key...
                                            differences
                                                declared
                                                real
                                    [not found]
                                        key...
                                    [not declared]
                                        key...
                                [matches]
                                    key...
                        [not found]
                            key...
                        [not declared]
                            key...
                    [matches]
                        key...
            [not found]
                key...
            [not declared]
                key...
        [matches]
            key...
matches
    [node...]
not found
    [node...]
not declared
    [node...]
```

### Result example
```json
{
    "differences": [
        {
            "differences": {
                "difference": {
                    "ports": {
                        "differences": {
                            "difference": {
                                "25": {
                                    "differences": {
                                        "difference": {
                                            "port": {
                                                "differences": {
                                                    "declared": 25,
                                                    "real": 26
                                                }
                                            }
                                        }
                                    },
                                    "matches": {
                                        "ip": "172.16.44.3",
                                        "name": "sw104"
                                    }
                                }
                            },
                            "not declared": {
                                "15": {
                                    "ip": "172.16.44.14",
                                    "name": "sw50",
                                    "port": 26
                                }
                            },
                            "not found": {
                                "26": {
                                    "ip": "172.16.44.13",
                                    "name": "sw51",
                                    "port": 26
                                }
                            }
                        },
                        "matches": {
                            "16": {
                                "ip": "172.16.44.19",
                                "name": "sw81",
                                "port": 26
                            }
                        }
                    }
                }
            },
            "matches": {
                "ip": "172.16.44.2",
                "name": "sw156"
            }
        }
    ],
    "matches": [
        {
            "ip": "172.16.44.8",
            "name": "sw102",
            "ports": {
                "25": {
                    "ip": "172.16.44.13",
                    "name": "sw62",
                    "port": 26
                }
            }
        }
    ],
    "not declared": [
        {
            "ip": "172.16.44.88",
            "name": "sw18",
            "ports": {
                "25": {
                    "ip": "172.16.44.13",
                    "name": "sw6",
                    "port": 26
                }
            }
        }
    ],
    "not found": []
}
```

