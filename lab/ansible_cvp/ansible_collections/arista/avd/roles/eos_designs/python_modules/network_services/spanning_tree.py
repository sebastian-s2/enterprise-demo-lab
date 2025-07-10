# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations

from functools import cached_property

from ansible_collections.arista.avd.plugins.filter.list_compress import list_compress
from ansible_collections.arista.avd.plugins.plugin_utils.utils import get
from ansible_collections.arista.avd.roles.eos_designs.python_modules.network_services.utils import UtilsMixin


class SpanningTreeMixin(UtilsMixin):
    """
    Mixin Class used to generate structured config for one key.
    Class should only be used as Mixin to a AvdStructuredConfig class
    """

    @cached_property
    def spanning_tree(self) -> dict | None:
        """
        spanning_tree priorities set per VLAN if spanning_tree mode is "rapid-pvst"
        """
        if not self.shared_utils.network_services_l2:
            return None

        spanning_tree_mode = get(self.shared_utils.switch_data_combined, "spanning_tree_mode")
        if spanning_tree_mode != "rapid-pvst":
            return None

        default_priority = int(get(self.shared_utils.switch_data_combined, "spanning_tree_priority", default=32768))

        vlan_stp_priorities = {}
        non_default_vlans = set()
        for tenant in self.shared_utils.filtered_tenants:
            for vrf in tenant["vrfs"]:
                for svi in vrf["svis"]:
                    if (priority := get(svi, "spanning_tree_priority")) is None:
                        continue
                    vlan_stp_priorities.setdefault(priority, set()).add(svi["id"])
                    non_default_vlans.add(svi["id"])
            for l2vlan in tenant["l2vlans"]:
                if (priority := get(l2vlan, "spanning_tree_priority")) is None:
                    continue
                vlan_stp_priorities.setdefault(priority, set()).add(l2vlan["id"])
                non_default_vlans.add(l2vlan["id"])

        if not non_default_vlans:
            # Quick return with only default
            return {"rapid_pvst_instances": [{"id": "1-4094", "priority": default_priority}]}

        default_vlans = non_default_vlans.symmetric_difference(range(1, 4094))
        vlan_stp_priorities.setdefault(default_priority, set()).update(default_vlans)
        return {
            "rapid_pvst_instances": [
                {
                    "id": list_compress(list(vlans)),
                    "priority": priority,
                }
                for priority, vlans in vlan_stp_priorities.items()
            ]
        }
