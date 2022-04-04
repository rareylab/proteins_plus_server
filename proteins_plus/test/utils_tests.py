"""tests for proteins_plus utility functions"""
from proteins_plus.test.utils import PPlusTestCase
from ..utils import json_to_sorted_string


class UtilTests(PPlusTestCase):
    """Utility tests"""

    def test_dict_list_to_unique_string(self):
        """Test converting dict and list to unique string for JSON"""
        self.assertEqual(json_to_sorted_string({}), '{}')
        self.assertEqual(json_to_sorted_string({'key': 1}), '{"key":1}')

        # sort keys
        self.assertEqual(json_to_sorted_string({'key': 1, 'afj': 'la'}), '{"afj":"la","key":1}')
        self.assertEqual(json_to_sorted_string({'afj': 'la', 'key': 1}), '{"afj":"la","key":1}')
        self.assertEqual(json_to_sorted_string({'b': 'A', 'a': 'B'}), '{"a":"B","b":"A"}')
        self.assertEqual(
            json_to_sorted_string({'b': 'A', 'a': {'c': 123}}), '{"a":{"c":123},"b":"A"}')
        self.assertEqual(
            json_to_sorted_string({'z': {'b': 123}, 'a': {'c': 123}}),
            '{"a":{"c":123},"z":{"b":123}}'
        )
        self.assertEqual(
            json_to_sorted_string({'a': {'j': {'b': 2, 'a': 0}, 'c': 1}}),
            '{"a":{"c":1,"j":{"a":0,"b":2}}}'
        )

        # sort lists
        self.assertEqual(json_to_sorted_string([]), '[]')
        self.assertEqual(json_to_sorted_string(['word']), '["word"]')
        self.assertEqual(json_to_sorted_string(['birne', 'apfel']), '["apfel","birne"]')
        self.assertEqual(json_to_sorted_string(['b', 'a', 'd', 'c']), '["a","b","c","d"]')

        # sort lists against primitives
        self.assertEqual(json_to_sorted_string(['b', ['d', 'a', 'c']]), '["b",["a","c","d"]]')
        self.assertEqual(json_to_sorted_string(['a', ['d', 'a', 'c']]), '["a",["a","c","d"]]')
        self.assertEqual(json_to_sorted_string(['b', ['d', 'a', ['c']]]), '["b",["a","d",["c"]]]')
        self.assertEqual(json_to_sorted_string(['b', [['c'], 'd', 'a']]), '["b",["a","d",["c"]]]')

        # sort objects against primitives
        self.assertEqual(json_to_sorted_string(['b', {}]), '["b",{}]')
        self.assertEqual(json_to_sorted_string(['b', {}, {}]), '["b",{},{}]')
        self.assertEqual(json_to_sorted_string(['b', {'a': 5, 'b': 'z'}]), '["b",{"a":5,"b":"z"}]')
        self.assertEqual(json_to_sorted_string({'f': ['c', 'b']}), '{"f":["b","c"]}')
        self.assertEqual(json_to_sorted_string({'f': ['c', {'b': 42}]}), '{"f":["c",{"b":42}]}')

        # sort objects against lists
        self.assertEqual(json_to_sorted_string([{}, 'a', []]), '["a",{},[]]')
        self.assertEqual(json_to_sorted_string([{'c': 1}, 'a', ['b']]), '["a",{"c":1},["b"]]')

        # sort objects against objects recursively
        self.assertEqual(
            json_to_sorted_string([{'a': {'b': 2}}, {'a': {'b': 1}}]),
            '[{"a":{"b":1}},{"a":{"b":2}}]'
        )
        self.assertEqual(
            json_to_sorted_string([{'a': {'c': 1}}, {'a': {'b': 1}}]),
            '[{"a":{"b":1}},{"a":{"c":1}}]'
        )
        self.assertEqual(json_to_sorted_string(
            [{'a': {'b': {}}}, {'a': {'b': 1}}]),
            '[{"a":{"b":1}},{"a":{"b":{}}}]'
        )
        self.assertEqual(json_to_sorted_string(
            [{'a': {'b': []}}, {'a': {'b': 1}}]),
            '[{"a":{"b":1}},{"a":{"b":[]}}]'
        )

        # handle circular references
        cyclic_dict = {'dict': {}}
        cyclic_dict['dict'] = cyclic_dict
        self.assertRaises(ValueError, json_to_sorted_string, cyclic_dict)

        cyclic_list = []
        cyclic_list.append(cyclic_list)
        self.assertRaises(ValueError, json_to_sorted_string, cyclic_list)

        # branching references are also forbidden
        branching_dict = {'dict': {}, 'otherDict': {}}
        another_dict = {}
        branching_dict['dict'] = another_dict
        branching_dict['otherDict'] = another_dict
        self.assertRaises(ValueError, json_to_sorted_string, branching_dict)

        # non JSON-like dict raise errors
        self.assertRaises(TypeError, json_to_sorted_string, {'key': set()})

    def test_unify_protein_site_dicts(self):
        # sort objects against objects
        self.assertEqual(json_to_sorted_string({'res_id': [
            {'name': 'ALA', 'pos': '123', 'chain': 'A'},

            {'name': 'THR', 'pos': '123', 'chain': 'A'},
            {'name': 'ALA', 'chain': 'A', 'pos': '123'},
        ]}),
            json_to_sorted_string({'res_id': [
                {'name': 'ALA', 'pos': '123', 'chain': 'A'},
                {'name': 'THR', 'pos': '123', 'chain': 'A'},
                {'name': 'ALA', 'chain': 'A', 'pos': '123'},
            ]}))

        self.assertEqual(json_to_sorted_string({'res_id': [
            {'name': 'ALA', 'pos': '123', 'chain': 'A'},
            {'name': 'ALA', 'chain': 'A', 'pos': '123'},
            {'name': 'THR', 'pos': '123', 'chain': 'A'},
        ]}),
            json_to_sorted_string({'res_id': [
                {'name': 'ALA', 'pos': '123', 'chain': 'A'},
                {'name': 'THR', 'pos': '123', 'chain': 'A'},
                {'name': 'ALA', 'chain': 'A', 'pos': '123'},
            ]}))

        self.assertEqual(json_to_sorted_string({'res_id': [
            {'name': 'ALA', 'pos': '123', 'chain': 'A'},
            {'chain': 'A', 'pos': '123', 'name': 'ALA', },
            {'name': 'THR', 'pos': '123', 'chain': 'A'},
        ]}),
            json_to_sorted_string({'res_id': [
                {'name': 'ALA', 'pos': '123', 'chain': 'A'},
                {'name': 'THR', 'pos': '123', 'chain': 'A'},
                {'name': 'ALA', 'chain': 'A', 'pos': '123'},
            ]}))

        self.assertEqual(json_to_sorted_string([
            {'name': 'ALA', 'pos': '123', 'chain': 'A'},
            {'chain': 'A', 'pos': '123', 'name': 'ALA', },
            {'name': 'THR', 'pos': '123', 'chain': 'A'},
        ]),
            json_to_sorted_string([
                {'name': 'ALA', 'pos': '123', 'chain': 'A'},
                {'name': 'THR', 'pos': '123', 'chain': 'A'},
                {'name': 'ALA', 'chain': 'A', 'pos': '123'},
            ]))

        self.assertNotEqual(json_to_sorted_string({'res_id': [
            {'name': 'ALA', 'pos': '123', 'chain': 'A'},
            {'chain': 'A', 'pos': '123', 'name': 'ALB', },
            {'name': 'THR', 'pos': '123', 'chain': 'A'},
        ]}),
            json_to_sorted_string({'res_id': [
                {'name': 'ALA', 'pos': '123', 'chain': 'A'},
                {'name': 'THR', 'pos': '123', 'chain': 'A'},
                {'name': 'ALA', 'chain': 'A', 'pos': '123'},
            ]}))
