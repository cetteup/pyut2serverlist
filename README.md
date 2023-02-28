# pyut2serverlist

[![ci](https://img.shields.io/github/actions/workflow/status/cetteup/pyut2serverlist/ci.yml?label=ci)](https://github.com/cetteup/pyut2serverlist/actions?query=workflow%3Aci)
[![License](https://img.shields.io/github/license/cetteup/pyut2serverlist)](/LICENSE)
[![Package](https://img.shields.io/pypi/v/pyut2serverlist)](https://pypi.org/project/pyut2serverlist/)
[![Last commit](https://img.shields.io/github/last-commit/cetteup/pyut2serverlist)](https://github.com/cetteup/pyut2serverlist/commits/main)

Simple Python library for querying Unreal Engine 2 based principal servers and their game servers

## Features
- retrieve a list of game servers from an Unreal Engine 2 principal ("master") server
- retrieve info directly from game servers

## Installation
Simply install the package via pip.

```bash
$ pip install pyut2serverlist
```

## Usage
The following example retrieves and prints a game server list for Unreal Tournament 2004 directly from Epic Games.

```python
from pyut2serverlist import PrincipalServer, Game, Error, Filter, Comparator

principal = PrincipalServer('utmaster.openspy.net', 28902, Game.UT2004, 'some-cd-key')

try:
    servers = principal.get_servers(
        Filter('gametype', Comparator.Equals, 'xDeathMatch')
    )
    print(servers)
except Error as e:
    print(e)
```

You can also directly initialize a game server object for a known server and query it to retrieve details such as the current map and game mode.

```python
from pyut2serverlist import Server, Error

server = Server('68.232.165.172', 7778)
try:
    info = server.get_info()
    print(info)
except Error as e:
    print(e)
```
