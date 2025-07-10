# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations

from functools import cached_property

from .utils import UtilsMixin


class RouteMapsMixin(UtilsMixin):
    """
    Mixin Class used to generate structured config for one key.
    Class should only be used as Mixin to a AvdStructuredConfig class
    """

    @cached_property
    def route_maps(self) -> list | None:
        """
        Return structured config for route_maps

        Contains two parts.
        - Route map for connected routes redistribution in BGP
        - Route map to filter peer AS in underlay
        """
        if not self.shared_utils.underlay_bgp and not self.shared_utils.is_wan_router:
            return None

        route_maps = []

        if self.shared_utils.overlay_routing_protocol != "none" and self.shared_utils.underlay_filter_redistribute_connected:
            # RM-CONN-2-BGP
            sequence_numbers = []
            sequence_10 = {
                "sequence": 10,
                "type": "permit",
                "match": ["ip address prefix-list PL-LOOPBACKS-EVPN-OVERLAY"],
            }
            if self.shared_utils.wan_role:
                sequence_10["set"] = [f"extcommunity soo {self.shared_utils.evpn_soo} additive"]

            sequence_numbers.append(sequence_10)

            # SEQ 20 is set by inband management if applicable, so avoid setting that here

            if self.shared_utils.underlay_ipv6 is True:
                sequence_numbers.append(
                    {
                        "sequence": 30,
                        "type": "permit",
                        "match": ["ipv6 address prefix-list PL-LOOPBACKS-EVPN-OVERLAY-V6"],
                    }
                )

            if self.shared_utils.underlay_multicast_rp_interfaces is not None:
                sequence_numbers.append(
                    {
                        "sequence": 40,
                        "type": "permit",
                        "match": ["ip address prefix-list PL-LOOPBACKS-PIM-RP"],
                    }
                )

            if self.shared_utils.wan_ha:
                sequence_numbers.append(
                    {
                        "sequence": 50,
                        "type": "permit",
                        "match": ["ip address prefix-list PL-WAN-HA-PREFIXES"],
                    }
                )

            route_maps.append({"name": "RM-CONN-2-BGP", "sequence_numbers": sequence_numbers})

        # RM-BGP-AS{{ asn }}-OUT
        for asn in self._underlay_filter_peer_as_route_maps_asns:
            route_map_name = f"RM-BGP-AS{asn}-OUT"
            route_maps.append(
                {
                    "name": route_map_name,
                    "sequence_numbers": [
                        {
                            "sequence": 10,
                            "type": "deny",
                            "match": [f"as {asn}"],
                        },
                        {
                            "sequence": 20,
                            "type": "permit",
                        },
                    ],
                }
            )

        # Route-map IN and OUT for SOO, rendered for WAN routers
        if self.shared_utils.underlay_routing_protocol == "ebgp" and self.shared_utils.wan_role == "client":
            # RM-BGP-UNDERLAY-PEERS-IN
            sequence_numbers = [
                {
                    "sequence": 40,
                    "type": "permit",
                    "description": "Mark prefixes originated from the LAN",
                    "set": [f"extcommunity soo {self.shared_utils.evpn_soo} additive"],
                },
            ]
            if self.shared_utils.wan_ha:
                sequence_numbers.extend(
                    [
                        {
                            "sequence": 10,
                            "type": "permit",
                            "description": "Allow WAN HA peer interface prefixes",
                            "match": ["ip address prefix-list PL-WAN-HA-PEER-PREFIXES"],
                        },
                        {
                            "sequence": 20,
                            "type": "permit",
                            "description": "Allow prefixes originated from the HA peer",
                            "match": ["extcommunity ECL-EVPN-SOO"],
                            "set": ["as-path match all replacement auto auto"],
                        },
                        {
                            "sequence": 30,
                            "type": "permit",
                            "description": "Use WAN routes from HA peer as backup",
                            "match": ["as-path ASPATH-WAN"],
                            "set": ["community no-advertise"],
                        },
                    ]
                )
            route_maps.append({"name": "RM-BGP-UNDERLAY-PEERS-IN", "sequence_numbers": sequence_numbers})

            # RM-BGP-UNDERLAY-PEERS-OUT
            sequence_numbers = [
                {
                    "sequence": 10,
                    "type": "permit",
                    "description": "Advertise local routes towards LAN",
                    "match": ["extcommunity ECL-EVPN-SOO"],
                },
                {
                    "sequence": 20,
                    "type": "permit",
                    "description": "Advertise routes received from WAN iBGP towards LAN",
                    "match": ["route-type internal"],
                },
            ]
            if self.shared_utils.wan_ha:
                sequence_numbers.append(
                    {
                        "sequence": 30,
                        "type": "permit",
                        "description": "Advertise WAN HA prefixes towards LAN",
                        "match": ["ip address prefix-list PL-WAN-HA-PREFIXES"],
                    },
                )
            route_maps.append({"name": "RM-BGP-UNDERLAY-PEERS-OUT", "sequence_numbers": sequence_numbers})

        if route_maps:
            return route_maps

        return None
