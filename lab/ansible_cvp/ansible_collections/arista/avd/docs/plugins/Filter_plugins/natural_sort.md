---
# This title is used for search results
title: arista.avd.natural_sort
---
<!--
  ~ Copyright (c) 2023-2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# natural_sort

!!! note
    Always use the FQCN (Fully Qualified Collection Name) `arista.avd.natural_sort` when using this plugin.

Sort an input list with natural sorting.

## Synopsis

Provides the capability to sort a list or a dictionary of integers and strings that contain alphanumeric characters naturally.
When leveraged on a dictionary, only the key value will be returned.
An optional `sort_key` can be specified, to sort on content of certain key if the items are dictionaries.

The filter will return an empty list if the value parsed to `arista.avd.natural_sort` is `None` or `undefined`.

## Parameters

| Argument | Type | Required | Default | Value Restrictions | Description |
| -------- | ---- | -------- | ------- | ------------------ | ----------- |
| <samp>_input</samp> | any | True | None |  | List or dictionary |
| <samp>sort_key</samp> | string | optional | None |  | Key to sort on when sorting a list of dictionaries |

## Examples

```yaml
---
sorted_list: "{{ ['test19', 'test9'] | natural_sort }}" # -> ["test9", "test19"]
sorted_keys: "{{ {'test19': 'value', 'test9': 'value'} | natural_sort }}" # -> ["test9", "test19"]
sorted_on_name_key: "{{ [{'name': 'test19'}, {'name': 'test9'}] | natural_sort('name') }}" # -> [{"name": "test9"}, {"name": "test19"}]
empty_list_1: "{{ none | natural_sort }}" # -> []
empty_list_2: "{{ some_undefined_var | natural_sort }}" # -> []
```

## Return Values

| Name | Type | Description |
| ---- | ---- | ----------- |
| _value | list | Sorted list if the input was a list. Sorted keys if the input was a dictionary. Empty list if the input value was `None` or `undefined`. |

## Authors

- Arista Ansible Team (@aristanetworks)
