# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import absolute_import, annotations, division, print_function

from ansible_collections.arista.avd.plugins.plugin_utils.errors.errors import AvdSchemaError

__metaclass__ = type

from copy import deepcopy

try:
    from referencing import Registry, Specification
    from referencing.exceptions import PointerToNowhere
    from referencing.jsonschema import DRAFT7, _legacy_anchor_in_dollar_id, _legacy_dollar_id, _maybe_in_subresource_crazy_items_dependencies

    HAS_REFERENCING = True
except ImportError:
    HAS_REFERENCING = False

from ansible_collections.arista.avd.plugins.plugin_utils.errors import AristaAvdError
from ansible_collections.arista.avd.plugins.plugin_utils.merge import merge


class AvdSchemaResolver:
    def __init__(self, base_schema_name: str, store: dict):
        if not HAS_REFERENCING:
            raise AristaAvdError('Python library "referencing" must be installed to use this plugin')

        self.resolver = self.create_resolver(store, base_uri=base_schema_name)

    def resolve(self, resolved_schema: dict):
        methods = {
            "items": self._items,
            "keys": self._keys,
            "dynamic_keys": self._dynamic_keys,
        }

        for key, method in methods.items():
            if resolved_schema.get(key):
                method(resolved_schema)

        return resolved_schema

    def _keys(self, resolved_schema: dict):
        for key in resolved_schema["keys"]:
            # Resolve the child schema
            # Repeat in case new refs inherited from the first ref.
            while "$ref" in resolved_schema["keys"][key]:
                self._ref_on_child(resolved_schema["keys"][key])

            self.resolve(resolved_schema["keys"][key])

    def _dynamic_keys(self, resolved_schema: dict):
        for key in resolved_schema["dynamic_keys"]:
            # Resolve the child schema
            # Repeat in case new refs inherited from the first ref.
            while "$ref" in resolved_schema["dynamic_keys"][key]:
                self._ref_on_child(resolved_schema["dynamic_keys"][key])

            self.resolve(resolved_schema["dynamic_keys"][key])

    def _items(self, resolved_schema: dict):
        # Resolve the child schema
        # Repeat in case new refs inherited from the first ref.
        while "$ref" in resolved_schema["items"]:
            self._ref_on_child(resolved_schema["items"])

        self.resolve(resolved_schema["items"])

    def _ref_on_child(self, resolved_schema: dict):
        """
        This function resolves the $ref referenced schema,
        then merges with any schema defined at the same level

        In place update of supplied resolved_schema
        """
        try:
            resolved = self.resolver.lookup(resolved_schema["$ref"])
        except PointerToNowhere:
            raise AvdSchemaError(
                (
                    f"Unable to resolve $ref: '{resolved_schema['$ref']}'."
                    "Make sure to adhere to the strict format '^(eos_cli_config_gen|eos_designs)#(/[a-z$][a-z0-9_]*)*$'."
                )
            ) from None
        ref_schema = deepcopy(resolved.contents)
        resolved_schema.pop("$ref")
        merge(resolved_schema, ref_schema, same_key_strategy="use_existing", list_merge="replace")

    def create_resolver(self, store: dict, base_uri=""):
        """
        Returns a resolver which can resolve "$ref" references across all AVD schemas.
        The given "base_uri" can be used for relative references (currently not used in AVD).
        """
        registry = self.create_registry(store)
        return registry.resolver(base_uri)

    @staticmethod
    def create_registry(store: dict) -> Registry:
        """
        Returns a "registry" for the "referencing" library.

        The registry contains schemas that could be resolved from references. In our case it
        contains the default jsonschema specifications + the AVD schemas.

        Since AVD uses a proprietary schema format, we have to declare a custom "specification"
        which contains functions used by the resolver to "walk" the schema.

        Since the AVD schema format is largely based on DRAFT7, we reuse some builtin functions
        from "referencing" which are also used for the builtin DRAFT7 specification.
        """

        def subresources(schema: dict):
            """
            Generator of childschemas
            """
            if "keys" in schema and schema["keys"]:
                yield from schema["keys"].values()
            if "dynamic_keys" in schema and schema["dynamic_keys"]:
                yield from schema["dynamic_keys"].values()
            if "$defs" in schema and schema["$defs"]:
                yield from schema["$defs"].values()
            if "items" in schema:
                yield schema["items"]

        avd_meta_schema_spec = Specification(
            name="avd_meta_schema",
            id_of=_legacy_dollar_id,
            subresources_of=subresources,
            anchors_in=_legacy_anchor_in_dollar_id,
            maybe_in_subresource=_maybe_in_subresource_crazy_items_dependencies(
                in_value=set(),
                in_subarray=set(),
                in_subvalues={"keys", "dynamic_keys", "$defs"},
            ),
        )
        resources = [
            ("avd_meta_schema", DRAFT7.create_resource(store["avd_meta_schema"])),
            ("eos_cli_config_gen", avd_meta_schema_spec.create_resource(store["eos_cli_config_gen"])),
            ("eos_designs", avd_meta_schema_spec.create_resource(store["eos_designs"])),
        ]
        return Registry().with_resources(resources)
