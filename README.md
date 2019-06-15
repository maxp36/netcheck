# netcheck
Comand-line utility to scan the network topology and find differences with a documented network structure

## Requirements

* [Python](https://www.python.org/) >= 3.5
* [MySQL](https://www.mysql.com/) >= 5.5

## Usage

1. Clone the repository

    ```bash
    git clone https://github.com/maxp36/netcheck.git
    ```

2. Go to directory and install python dependencies

    ```bash
    cd netcheck/
    pip install -r requirements.txt
    ```
3. Edit the configuration files in ./config directory

4. Run netcheck

    ```bash
    ./netcheck.py
    ```

## Comand exapmles
To show the help message run
```bash
./netcheck.py
```
or
```bash
./netcheck.py -h
```

To perform a network scan and save the result to a file run
1. to scan real topology:
    ```bash
    ./netcheck.py store real
    ```
2. to scan declared topology:
    ```bash
    ./netcheck.py store declared
    ```

To scan the real and documented network, compare the topologies and write the comparison result to a file run
```bash
./netcheck.py nms
```

To compare the topologies described in the input files and save the result to a file run
```bash
./netcheck.py cmp PATH1 PATH2
```

For more informatioon about operation run
```bash
./netcheck.py OPERATION -h
```

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

    snmp: {
        community: community
    }

    hosts: [
        host1_address
        host2_address
    ]

    aliases: {
        host_name: host_address
    }

    limitations: {
        host1_address: {
            check_ports: [port1, port2]
            exclude_ports: [port3]
        }
        host2_address: {
            exclude_ports: [port1]
        }
    }
}
```

### Configuration file description
The configuration file contains two objects at the top level:

1. `db` - an object containing information about connecting to the database containing information about switches (required)
    1. `host` - address to connect to the database (required)
    2. `user` - db login username (required)
    3. `pass` - db login password (required)
    4. `name` - database name (required)

2. `snmp` - an object containing SNMP connecting information (required)
    1. `community` - SNMP community parameter

3. `hosts` - an array of ipv4 addresses from which to start scanning the network (required)

4. `aliases` - object containing information about the mapping of the name of the switch and its permanent ipv4 address

5. `limitations` - object containing additional scanning limitations for `host_address` object

    Each `host_address` object contains the following fields:

    1. `check_ports` - an array of port numbers from which you want to continue scanning neighbor switches
    2. `exclude_ports` - an array of port numbers from which scanning of neighbor switches should not continue

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
`field...` means array of field.
```
found
    [host...]
        differences
            [key...]
                declared
                real
        matches
            [key...]
        not declared
            [key...]
        not found
            [key...]
not declared
    [host...]
        key...
not found
    [host...]
        key...
```

### Result example
```json
{
    "found": {
        "172.16.44.9": {
            "differences": {
                "ports": {
                    "26": {
                        "port": {
                            "declared": 26,
                            "real": 25
                        }
                    }
                }
            },
            "matches": {
                "ip": "172.16.44.9",
                "name": "sw168",
                "ports": {
                    "25": {
                        "ip": "172.16.44.13",
                        "name": "sw62",
                        "port": 27
                    },
                    "26": {
                        "ip": "172.16.44.10",
                        "name": "sw76"
                    }
                }
            },
            "not declared": {
                "ports": {
                    "27": {
                        "ip": "172.16.44.16",
                        "name": "sw63",
                        "port": 25
                    }
                }
            },
            "not found": {
                "ports": {
                    "28": {
                        "ip": "172.16.44.78",
                        "name": "sw06102",
                        "port": 27
                    }
                }
            }
        }
    },
    "not declared": {
        "172.16.44.777": {
            "ip": "172.16.44.777",
            "name": "sw777",
            "ports": {
                "25": {
                    "ip": "172.16.44.14",
                    "name": "sw50",
                    "port": 26
                }
            }
        }
    },
    "not found": {
        "172.16.44.188": {
            "ip": "172.16.44.188",
            "name": "sw64333",
            "ports": {
                "26": {
                    "ip": "172.16.44.14",
                    "name": "sw50",
                    "port": 26
                }
            }
        }
    }
}
```
