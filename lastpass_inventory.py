#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0
"""Populate a Ansible inventory with information from LastPass."""
import os
import shutil
import subprocess
import sys
import argparse
from urllib.parse import urlparse
import yaml

__metaclass__ = type

DOCUMENTATION = """
    name: lastpass_inventory
    author:
      - Thomas Sjögren (@konstruktoid)
    short_description: Populate a Ansible inventory with information from LastPass.
    description:
      - Populates a Ansible inventory with information from LastPass.
      - Uses a YAML configuration file lastpass_inventory.yml.
"""

EXAMPLES = """
# lastpass_inventory.yml configuration file:
---
lastpass_hosts:
    test-server-01: test-server-01
    test-server-02: test-server-02
    webserver: test-server-01
    database: "7815456364361241116"
...
"""

try:
    import json
except ImportError:
    import simplejson as json

__version__ = "0.0.1"


class AnsibleLastPassInventory:
    """The AnsibleLastPassInventory class."""

    def __init__(self):
        self.lastpass_cmd = shutil.which("lpass")
        self.inventory = {}
        self.inventory_content = {}
        self.generated_inventory = {}
        self.read_cli_args()
        self.ensure_lastpass()
        self.generate_inventory()

    def generate_inventory(self):
        """Generate the inventory."""
        try:
            self.configuration_file = os.getcwd() + "/lastpass_inventory.yml"

            if not os.path.isfile(self.configuration_file):
                print(self.configuration_file + " can't be found.")
                sys.exit(1)
            else:
                with open(
                    "./lastpass_inventory.yml", "r", encoding="utf-8"
                ) as inventory_file:
                    self.inventory = yaml.safe_load(inventory_file)

            self.generated_inventory = self.inventory_content
            self.inventory_content["lastpass_hosts"] = []
            self.inventory_content["_meta"] = {}
            self.inventory_content["_meta"]["hostvars"] = {}

            for inventory in self.inventory.values():
                for name, identifier in inventory.items():
                    host_lpass_json = json.loads(
                        subprocess.run(
                            [self.lastpass_cmd, "show", identifier, "--json"],
                            shell=False,
                            check=True,
                            text=True,
                            capture_output=True,
                        ).stdout
                    )

                    self.inventory_content["lastpass_hosts"].append(name)
                    self.inventory_content["_meta"]["hostvars"][name] = {}
                    self.inventory_content["_meta"]["hostvars"][name][
                        "ansible_user"
                    ] = host_lpass_json[0]["username"]
                    self.inventory_content["_meta"]["hostvars"][name][
                        "ansible_password"
                    ] = host_lpass_json[0]["password"]
                    self.inventory_content["_meta"]["hostvars"][name][
                        "ansible_host"
                    ] = urlparse(host_lpass_json[0]["url"]).netloc

        except subprocess.CalledProcessError as exception:
            print("There was an issue with:\n  " + name + ": " + identifier)
            print(exception)
            sys.exit(1)

        if self.args.list:
            print(json.dumps(self.generated_inventory, sort_keys=True, indent=2))
        else:
            print(json.dumps(self.generated_inventory, sort_keys=True))

    def ensure_lastpass(self):
        """Ensure LastPass is installed and the user is logged in."""
        try:
            if not self.lastpass_cmd:
                print("lpass doesn't seem to be installed. Exiting.")
                sys.exit(1)

            if not subprocess.check_output([self.lastpass_cmd, "ls"], shell=False):
                sys.exit(1)

        except Exception as exception_string:
            print("Exception: ", str(exception_string), file=sys.stderr)
            sys.exit(1)

    def list_lastpass_vault(self):
        """Test the lpass ls function."""
        try:
            subprocess.run([self.lastpass_cmd, "ls"], shell=False, check=True)

        except Exception as exception_string:
            print("Exception: ", str(exception_string), file=sys.stderr)
            sys.exit(1)

    def read_cli_args(self):
        """Command line arguments and help information."""

        parser = argparse.ArgumentParser(
            description="Populate a Ansible inventory with information from LastPass.",
            epilog="version: " + __version__,
        )
        parser.add_argument(
            "-l",
            "--list",
            help="print the inventory",
            action="store_true",
        )

        self.args = parser.parse_args()


AnsibleLastPassInventory()
