# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations

from collections import defaultdict
from functools import cached_property

from .utils import UtilsMixin


class IpNatMixin(UtilsMixin):
    """
    Mixin Class used to generate structured config for one key.
    Class should only be used as Mixin to a AvdStructuredConfig class
    """

    @cached_property
    def ip_nat(self) -> dict | None:
        """
        Returns structured config for ip_nat
        """
        if not self.shared_utils.is_cv_pathfinder_client:
            return None

        ip_nat = defaultdict(list)

        policy_types = sorted(set(internet_exit_policy["type"] for internet_exit_policy in self._filtered_internet_exit_policies))

        for policy_type in policy_types:
            pool, profile = self.get_internet_exit_nat_pool_and_profile(policy_type)
            if pool:
                ip_nat["pools"].append(pool)
            if profile:
                ip_nat["profiles"].append(profile)

        if ip_nat:
            return ip_nat

        return None
