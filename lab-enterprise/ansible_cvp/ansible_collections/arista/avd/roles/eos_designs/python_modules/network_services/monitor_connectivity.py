# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations

from functools import cached_property

from ansible_collections.arista.avd.plugins.plugin_utils.strip_empties import strip_empties_from_dict
from ansible_collections.arista.avd.plugins.plugin_utils.utils import append_if_not_duplicate

from .utils import UtilsMixin


class MonitorConnectivityMixin(UtilsMixin):
    """
    Mixin Class used to generate structured config for one key.
    Class should only be used as Mixin to a AvdStructuredConfig class
    """

    @cached_property
    def monitor_connectivity(self) -> dict | None:
        """
        Return structured config for monitor_connectivity

        Only used for CV Pathfinder edge routers today
        """
        if not self._filtered_internet_exit_policies:
            return None

        monitor_connectivity = {}
        interface_sets = []
        hosts = []

        for policy in self._filtered_internet_exit_policies:
            for connection in policy["connections"]:
                if connection["type"] == "tunnel":
                    interface_name = f"Tunnel{connection['tunnel_id']}"
                else:
                    interface_name = connection["source_interface"]

                interface_set_name = f"SET-{self.shared_utils.sanitize_interface_name(interface_name)}"
                interface_sets.append(
                    {
                        "name": interface_set_name,
                        "interfaces": interface_name,
                    }
                )

                host = {
                    "name": connection["monitor_name"],
                    "description": connection["description"],
                    "ip": connection["monitor_host"],
                    "local_interfaces": interface_set_name,
                    "address_only": False,
                    "url": connection.get("monitor_url"),
                }
                append_if_not_duplicate(
                    list_of_dicts=hosts,
                    primary_key="name",
                    new_dict=host,
                    context="Monitor connectivity host for Internet Exit policy",
                    context_keys=["name"],
                )

        monitor_connectivity["interface_sets"] = interface_sets
        monitor_connectivity["hosts"] = hosts

        monitor_connectivity = strip_empties_from_dict(monitor_connectivity)

        if monitor_connectivity:
            monitor_connectivity["shutdown"] = False
            return monitor_connectivity

        return None
