"""utils for proteins_plus app"""
from copy import deepcopy
import json
from functools import cmp_to_key


def compare_json_dict(first, second):
    """JSON dict comparator

    Used in conjunction with compare_json_value

    :note: circular object references are not legal in JSON and will lead to infinite recursion.
    :param first: first dict
    :param second: second dict
    :return: -1, 0 or 1 meaning sort a before b, a and b are not comparable, sort b before a
    """
    for a_key, b_key in zip(sorted(first.keys()), sorted(second.keys())):
        if a_key != b_key:
            return -1 if a_key < b_key else 1

        comparison = compare_json_value(first[a_key], second[b_key])
        if comparison != 0:
            return comparison
    return 0


def compare_json_value(first, second):
    """JSON value sort comparator

    Can handle all JSON legal values.

    :note: circular object references are not legal in JSON and will lead to infinite recursion.
    :param first: first value
    :param second: second value
    :return: -1, 0 or 1 meaning sort a before b, a and b are not comparable, sort b before a
    """
    if isinstance(first, list) and not isinstance(second, list):
        return 1
    if not isinstance(first, list) and isinstance(second, list):
        return -1
    if isinstance(first, dict) and not isinstance(second, dict):
        return 1
    if not isinstance(first, dict) and isinstance(second, dict):
        return -1
    if isinstance(first, dict) and isinstance(second, dict):
        return compare_json_dict(first, second)
    if first != second:
        return -1 if first < second else 1
    return 0


def sort_json_lists(obj):
    """Recursively sort all lists in the JSON in place

    :param obj: currently recursed on JSON object
    :type obj: object
    """

    def sort_json_lists_recursive(current_obj):
        values = []
        if isinstance(current_obj, list):
            if id(current_obj) in seen_objects:
                raise ValueError('Circular reference detected')
            seen_objects.add(id(current_obj))
            current_obj.sort(key=cmp_to_key(compare_json_value))
            values = current_obj
        elif isinstance(current_obj, dict):
            if id(current_obj) in seen_objects:
                raise ValueError('Circular reference detected')
            seen_objects.add(id(current_obj))
            values = current_obj.values()
        for value in values:
            sort_json_lists_recursive(value)

    seen_objects = set()
    sort_json_lists_recursive(obj)


def json_to_sorted_string(obj, copy=True):
    """Converts nested json object to sorted string.

    Can be used to uniquely identify JSON files for hashing and caching. The resulting string is a
    unique representation of the nested contents of the object.

    :param obj: the object
    :type obj: object
    :param copy: Whether to copy obj before sorting.
    :type copy: bool
    :return A unique string
    """
    this_obj = obj
    if copy:
        this_obj = deepcopy(this_obj)
    sort_json_lists(this_obj)
    return json.dumps(this_obj, sort_keys=True, separators=(',', ':'))
