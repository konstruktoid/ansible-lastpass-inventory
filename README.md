# Dynamic LastPass Ansible Inventory

Requires a [LastPass](https://www.lastpass.com/) account and the [lpass](https://github.com/lastpass/lastpass-cli)
client.

The `lastpass_inventory.py` script uses the `lastpass_inventory.yml`
configuration file to fetch the named servers from the current logged in
LastPass account using `lpass`, and then generate an [Ansible](https://www.ansible.com/)
inventory.

## Examples and Usage

The `lastpass_inventory.yml` configuration file names and fetches the hosts
using `name: identifier`, where the `name` variable is what the host will be
named in the inventory and the `identifier` is used to identify the host in
LastPass.

Both the name and the ID number from e.g. `lpass ls` can be used as an
identifier for a host.

Note that the script will fail if the name or ID is incorrect or missing.

The LastPass `user` and `password` fields will be used to populate
`ansible_user` and `ansible_password`.
The `ansible_host` address is the extracted netloc from the LastPass `url` field
using [urllib.parse.urlparse](https://docs.python.org/3/library/urllib.parse.html).

Example `lpass ls` output:

```console
servers
    ansible-managed
        test-server-01 [id: 3024014487647346952]
        test-server-02 [id: 7815456364361241116]
```

Configuration file based on the above output:

```yaml
---
lastpass_hosts:
    test-server-01: test-server-01
    test-server-02: test-server-02
    webserver: test-server-01
    database: "7815456364361241116"
...
```

Running `ansible-inventory -i lastpass_inventory.py --list --yaml` will then
generate the following inventory:

```yaml
all:
  children:
    lastpass_hosts:
      hosts:
        database:
          ansible_host: 10.0.1.2
          ansible_password: SuperSecretLastPass
          ansible_user: ansibleuser
        test-server-01:
          ansible_host: 10.0.1.1
          ansible_password: SuperSecretLastPass
          ansible_user: ansibleuser
        test-server-02:
          ansible_host: 10.0.1.2
          ansible_password: SuperSecretLastPass
          ansible_user: ansibleuser
        webserver:
          ansible_host: 10.0.1.1
          ansible_password: SuperSecretLastPass
          ansible_user: ansibleuser
    ungrouped: {}
```
