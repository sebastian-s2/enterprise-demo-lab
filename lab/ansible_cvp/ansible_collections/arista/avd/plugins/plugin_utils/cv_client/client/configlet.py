# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from ..api.arista.configlet.v1 import (
    Configlet,
    ConfigletAssignment,
    ConfigletAssignmentConfig,
    ConfigletAssignmentConfigServiceStub,
    ConfigletAssignmentConfigSetRequest,
    ConfigletAssignmentConfigSetSomeRequest,
    ConfigletAssignmentKey,
    ConfigletAssignmentServiceStub,
    ConfigletAssignmentStreamRequest,
    ConfigletConfig,
    ConfigletConfigServiceStub,
    ConfigletConfigSetRequest,
    ConfigletConfigSetSomeRequest,
    ConfigletKey,
    ConfigletServiceStub,
    ConfigletStreamRequest,
    MatchPolicy,
)
from ..api.fmp import RepeatedString
from .exceptions import get_cv_client_exception

if TYPE_CHECKING:
    from .cv_client import CVClient


ASSIGNMENT_MATCH_POLICY_MAP = {
    "match_first": MatchPolicy.MATCH_FIRST,
    "match_all": MatchPolicy.MATCH_ALL,
    None: MatchPolicy.UNSPECIFIED,
}


class ConfigletMixin:
    """
    Only to be used as mixin on CVClient class.
    """

    configlet_api_version: Literal["v1"] = "v1"

    async def get_configlet_containers(
        self: CVClient,
        workspace_id: str,
        container_ids: list[str] | None = None,
        time: datetime | None = None,
        timeout: float = 10.0,
    ) -> list[ConfigletAssignment]:
        """
        Get Configlet Containers (a.k.a. Assignments) using arista.configlet.v1.ConfigletAssignmentServiceStub.GetAll API.

        Parameters:
            workspace_id: Unique identifier of the Workspace for which the information is fetched. Use "" for mainline.
            container_ids: Unique identifiers for Containers/Assignments.
            time: Timestamp from which the information is fetched. `now()` if not set.
            timeout: Timeout in seconds.

        Returns:
            ConfigletAssignment objects.
        """
        request = ConfigletAssignmentStreamRequest(partial_eq_filter=[], time=time)
        if container_ids:
            for container_id in container_ids:
                request.partial_eq_filter.append(
                    ConfigletAssignment(key=ConfigletAssignmentKey(workspace_id=workspace_id, configlet_assignment_id=container_id))
                )
        else:
            request.partial_eq_filter.append(ConfigletAssignment(key=ConfigletAssignmentKey(workspace_id=workspace_id)))

        client = ConfigletAssignmentServiceStub(self._channel)
        configlet_assignments = []
        try:
            responses = client.get_all(request, metadata=self._metadata, timeout=timeout)
            async for response in responses:
                configlet_assignments.append(response.value)
            return configlet_assignments

        except Exception as e:
            raise get_cv_client_exception(e, f"Workspace ID '{workspace_id}', ConfigletAssignment ID '{container_ids}'") or e

    async def set_configlet_container(
        self: CVClient,
        workspace_id: str,
        container_id: str,
        display_name: str | None = None,
        description: str | None = None,
        configlet_ids: list[str] | None = None,
        query: str | None = None,
        child_assignment_ids: list[str] | None = None,
        match_policy: Literal["match_first", "match_all"] = "match_all",
        timeout: float = 10.0,
    ) -> ConfigletAssignmentConfig:
        """
        Create/update a Configlet Container (a.k.a. Assignment) using arista.configlet.v1.ConfigletAssignmentServiceStub.Set API.

        Parameters:
            workspace_id: Unique identifier of the Workspace for which the information is fetched.
            container_id: Unique identifier for Container/Assignment.
            display_name: Container/Assignment Name.
            description: Container/Assignment description.
            timeout: Timeout in seconds.

        Returns:
            ConfigletAssignmentConfig object after being set including any server-generated values.
        """
        request = ConfigletAssignmentConfigSetRequest(
            value=ConfigletAssignmentConfig(
                key=ConfigletAssignmentKey(workspace_id=workspace_id, configlet_assignment_id=container_id),
                display_name=display_name,
                description=description,
                configlet_ids=RepeatedString(values=configlet_ids),
                query=query,
                child_assignment_ids=RepeatedString(values=child_assignment_ids),
                match_policy=ASSIGNMENT_MATCH_POLICY_MAP.get(match_policy),
            )
        )
        client = ConfigletAssignmentConfigServiceStub(self._channel)
        try:
            response = await client.set(request, metadata=self._metadata, timeout=timeout)
            return response.value

        except Exception as e:
            raise get_cv_client_exception(e, f"Workspace ID '{workspace_id}', ConfigletAssignment ID '{container_id}'") or e

    async def set_configlet_containers(
        self: CVClient,
        workspace_id: str,
        containers: list[tuple[str, str | None, str | None, list[str] | None, str | None, list[str] | None, str | None]],
        timeout: float = 30.0,
    ) -> list[ConfigletAssignmentKey]:
        """
        Create/update a Configlet Container (a.k.a. Assignment) using arista.configlet.v1.ConfigletAssignmentServiceStub.Set API.

        Parameters:
            workspace_id: Unique identifier of the Workspace for which the information is fetched.
            containers: List of Tuples with the format\
                (container_id, display_name, description, configlet_ids, query, list_of_configlet_ids, match_policy).
            timeout: Base timeout in seconds. 0.5 second will be added per container.

        Returns:
            ConfigletAssignmentKey objects after being set including any server-generated values.
        """

        request = ConfigletAssignmentConfigSetSomeRequest(
            values=[
                ConfigletAssignmentConfig(
                    key=ConfigletAssignmentKey(workspace_id=workspace_id, configlet_assignment_id=container_id),
                    display_name=display_name,
                    description=description,
                    configlet_ids=RepeatedString(values=configlet_ids),
                    query=query,
                    child_assignment_ids=RepeatedString(values=child_assignment_ids),
                    match_policy=ASSIGNMENT_MATCH_POLICY_MAP.get(match_policy),
                )
                for container_id, display_name, description, configlet_ids, query, child_assignment_ids, match_policy in containers
            ]
        )
        client = ConfigletAssignmentConfigServiceStub(self._channel)
        assignment_keys = []
        try:
            responses = client.set_some(request, metadata=self._metadata, timeout=timeout + len(request.values) * 0.5)
            async for response in responses:
                assignment_keys.append(response.key)

            return assignment_keys

        except Exception as e:
            raise get_cv_client_exception(e, f"Workspace ID '{workspace_id}', Containers '{containers}'") or e

    async def delete_configlet_container(
        self: CVClient,
        workspace_id: str,
        assignment_id: str,
        timeout: float = 10.0,
    ) -> ConfigletAssignmentConfig:
        """
        Delete a Configlet Container (a.k.a. Assignment) using arista.configlet.v1.ConfigletAssignmentServiceStub.Set API.

        Parameters:
            workspace_id: Unique identifier of the Workspace for which the information is fetched.
            assignment_id: Unique identifier for Container/Assignment.

        Returns:
            ConfigletAssignmentConfig object after being set including any server-generated values.
        """
        request = ConfigletAssignmentConfigSetRequest(
            value=ConfigletAssignmentConfig(
                key=ConfigletAssignmentKey(workspace_id=workspace_id, configlet_assignment_id=assignment_id),
                remove=True,
            )
        )
        client = ConfigletAssignmentConfigServiceStub(self._channel)
        try:
            response = await client.set(request, metadata=self._metadata, timeout=timeout)
            return response.value

        except Exception as e:
            raise get_cv_client_exception(e, f"Workspace ID '{workspace_id}', ConfigletAssignment ID '{assignment_id}'") or e

    async def get_configlets(
        self: CVClient,
        workspace_id: str,
        configlet_ids: list[str] | None = None,
        time: datetime | None = None,
        timeout: float = 10.0,
    ) -> list[Configlet]:
        """
        Get Configlets using arista.configlet.v1.ConfigletServiceStub.GetAll API.
        Missing objects will not produce an error.

        Parameters:
            workspace_id: Unique identifier of the Workspace for which the information is fetched. Use "" for mainline.
            configlet_ids: Unique identifiers for Configlets. If not set the function will return all configlets.
            time: Timestamp from which the information is fetched. `now()` if not set.
            timeout: Timeout in seconds.

        Returns:
            List of matching Configlet objects.
        """
        request = ConfigletStreamRequest(partial_eq_filter=[], time=time)
        if configlet_ids:
            for configlet_id in configlet_ids:
                request.partial_eq_filter.append(Configlet(key=ConfigletKey(workspace_id=workspace_id, configlet_id=configlet_id)))
        else:
            request.partial_eq_filter.append(Configlet(key=ConfigletKey(workspace_id=workspace_id)))

        client = ConfigletServiceStub(self._channel)
        configlets = []
        try:
            responses = client.get_all(request, metadata=self._metadata, timeout=timeout)
            async for response in responses:
                configlets.append(response.value)

            return configlets

        except Exception as e:
            raise get_cv_client_exception(e, f"Workspace ID '{workspace_id}', Configlet IDs '{configlet_ids}'") or e

    async def set_configlet(
        self: CVClient,
        workspace_id: str,
        configlet_id: str,
        display_name: str | None = None,
        description: str | None = None,
        body: str | None = None,
        timeout: float = 10.0,
    ) -> ConfigletConfig:
        """
        Create/update a Configlet using arista.configlet.v1.ConfigletServiceStub.Set API.

        Parameters:
            workspace_id: Unique identifier of the Workspace for which the information is fetched.
            configlet_id: Unique identifier for Configlet.
            display_name: Configlet Name.
            description: Configlet description.
            body: EOS Configuration.
            timeout: Timeout in seconds.

        Returns:
            ConfigletAssignment object after being set including any server-generated values.
        """
        request = ConfigletConfigSetRequest(
            value=ConfigletConfig(
                key=ConfigletKey(workspace_id=workspace_id, configlet_id=configlet_id),
                display_name=display_name,
                description=description,
                body=body,
            )
        )
        client = ConfigletConfigServiceStub(self._channel)
        try:
            response = await client.set(request, metadata=self._metadata, timeout=timeout)
            return response.value

        except Exception as e:
            raise get_cv_client_exception(e, f"Workspace ID '{workspace_id}', Configlet ID '{configlet_id}'") or e

    async def set_configlet_from_file(
        self: CVClient,
        workspace_id: str,
        configlet_id: str,
        file: str,
        display_name: str | None = None,
        description: str | None = None,
        timeout: float = 10.0,
    ) -> ConfigletConfig:
        """
        Create/update a Configlet using arista.configlet.v1.ConfigletServiceStub.Set API.

        Parameters:
            workspace_id: Unique identifier of the Workspace for which the information is fetched.
            configlet_id: Unique identifier for Configlet.
            file: Path to file containing EOS Configuration.
            display_name: Configlet Name.
            description: Configlet description.
            timeout: Timeout in seconds.

        Returns:
            ConfigletConfig object after being set including any server-generated values.
        """
        request = ConfigletConfigSetRequest(
            value=ConfigletConfig(
                key=ConfigletKey(workspace_id=workspace_id, configlet_id=configlet_id),
                display_name=display_name,
                description=description,
                body=Path(file).read_text(encoding="UTF-8"),
            )
        )
        client = ConfigletConfigServiceStub(self._channel)
        try:
            response = await client.set(request, metadata=self._metadata, timeout=timeout)
            return response.value

        except Exception as e:
            raise get_cv_client_exception(e, f"Workspace ID '{workspace_id}', Configlet ID '{configlet_id}', File '{file}'") or e

    async def delete_configlets(
        self: CVClient,
        workspace_id: str,
        configlet_ids: list[str],
        timeout: float = 30.0,
    ) -> list[ConfigletKey]:
        """
        Delete a Configlet using arista.configlet.v1.ConfigletServiceStub.SetSome API.

        Parameters:
            workspace_id: Unique identifier of the Workspace for which the information is fetched.
            configlet_ids: List of unique identifiers for Configlets to delete.
            timeout: Timeout in seconds.

        Returns:
            List of ConfigletKey objects after being deleted including any server-generated values.
        """
        request = ConfigletConfigSetSomeRequest(values=[])
        for configlet_id in configlet_ids:
            request.values.append(
                ConfigletConfig(
                    key=ConfigletKey(workspace_id=workspace_id, configlet_id=configlet_id),
                    remove=True,
                )
            )
        client = ConfigletConfigServiceStub(self._channel)

        configlet_configs = []
        try:
            responses = client.set_some(request, metadata=self._metadata, timeout=timeout)
            async for response in responses:
                configlet_configs.append(response.key)

            return configlet_configs
        except Exception as e:
            raise get_cv_client_exception(e, f"Workspace ID '{workspace_id}', Configlet IDs '{configlet_ids}'") or e
