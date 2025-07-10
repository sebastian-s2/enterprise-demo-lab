# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations

from functools import cached_property

from .utils import UtilsMixin


class AsPathMixin(UtilsMixin):
    """
    Mixin Class used to generate structured config for one key.
    Class should only be used as Mixin to a AvdStructuredConfig class
    """

    @cached_property
    def as_path(self) -> list | None:
        """
        Return structured config for as_path.
        """
        if self.shared_utils.underlay_routing_protocol != "ebgp":
            return None

        access_lists = []
        if self.shared_utils.is_cv_pathfinder_client:
            access_lists.append(
                {
                    "name": "ASPATH-WAN",
                    "entries": [
                        {
                            "type": "permit",
                            "match": self.shared_utils.bgp_as,
                        },
                    ],
                }
            )

        if access_lists:
            return {"access_lists": access_lists}

        return None
