# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations

from functools import cached_property

from .utils import UtilsMixin


class DpsInterfacesMixin(UtilsMixin):
    """
    Mixin Class used to generate structured config for one key.
    Class should only be used as Mixin to a AvdStructuredConfig class
    """

    @cached_property
    def dps_interfaces(self) -> list | None:
        """
        Returns structured config for dps_interfaces

        Only used for WAN devices
        """
        if not self.shared_utils.is_wan_router:
            return None

        dps1 = {
            "name": "Dps1",
            "description": "DPS Interface",
            # Recommended MTU value to avoid double fragmentation in certain cases
            "mtu": 9214,
        }

        if self.shared_utils.vtep_loopback.lower().startswith("dps"):
            dps1["ip_address"] = f"{self.shared_utils.vtep_ip}/32"

        # TODO do IPv6 when needed - for now no easy way in AVD to detect if this is needed
        # When needed - need a default value if different than IPv4

        if (dpsFlow := self.shared_utils.get_flow_tracker(None, "dps_interfaces")) is not None:
            dps1["flow_tracker"] = dpsFlow

        return [dps1]
