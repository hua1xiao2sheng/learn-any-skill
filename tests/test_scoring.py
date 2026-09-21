"""Regression tests for the offline scoring helper."""
import copy
import json
import math
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts._common import DataError, load_json, number
from scripts.score_resources import DEFAULT_WEIGHTS, normalize, rank_resources, render_markdown


def resource(name="item", score=4):
    return {"name": name, "scores": {key: score for key in DEFAULT_WEIGHTS}}


class ScoringTests(unittest.TestCase):
    def test_original_fixture_order_and_values(self):
        result = rank_resources(load_json(ROOT / 'examples/resources.example.json'))
        self.assertEqual([r['total_score'] for r in result['resources']], [90.0, 89.0, 68.0])

    def test_preserves_schema_and_fixture_metadata(self):
        payload = load_json(ROOT / 'examples/resources.example.json')
        result = rank_resources(payload)
        self.assertEqual(result['schema_version'], '0.2')
        self.assertIs(result['is_fixture'], True)

    def test_ranked_ledger_still_matches_its_schema(self):
        from jsonschema import Draft202012Validator
        schema = load_json(ROOT / 'schemas/resources.schema.json')
        result = rank_resources(load_json(ROOT / 'examples/resources.example.json'))
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(result)), [])

    def test_legacy_array_input(self):
        self.assertEqual(rank_resources([resource()])['resources'][0]['total_score'], 80)

    def test_default_weights_sum_to_one(self):
        _, weights = normalize([resource()])
        self.assertAlmostEqual(sum(weights.values()), 1)

    def test_partial_custom_weights_are_merged_then_normalized(self):
        _, weights = normalize({'resources': [resource()], 'weights': {'authority': 1}})
        self.assertAlmostEqual(weights['authority'], 1 / 1.8)
        self.assertAlmostEqual(weights['relevance'], .25 / 1.8)

    def test_empty_mapping_means_default_weights(self):
        self.assertEqual(normalize({'resources': [resource()], 'weights': {}})[1], normalize([resource()])[1])

    def test_bad_weight_container_is_rejected_even_when_falsy(self):
        for value in [[], None, False, 0, '']:
            with self.subTest(value=value), self.assertRaises(DataError):
                normalize({'resources': [resource()], 'weights': value})

    def test_boolean_weights_are_rejected(self):
        with self.assertRaises(DataError):
            normalize({'resources': [resource()], 'weights': {'authority': True}})

    def test_boolean_scores_are_rejected(self):
        with self.assertRaises(DataError):
            rank_resources([resource(score=True)])

    def test_nonfinite_weights_are_rejected(self):
        for value in [math.nan, math.inf, -math.inf]:
            with self.subTest(value=value), self.assertRaises(DataError):
                normalize({'resources': [resource()], 'weights': {'authority': value}})

    def test_nonfinite_scores_are_rejected(self):
        for value in [math.nan, math.inf, -math.inf]:
            with self.subTest(value=value), self.assertRaises(DataError):
                rank_resources([resource(score=value)])

    def test_zero_total_weights_are_rejected(self):
        with self.assertRaises(DataError):
            normalize({'resources': [resource()], 'weights': dict.fromkeys(DEFAULT_WEIGHTS, 0)})

    def test_negative_weight_is_rejected(self):
        with self.assertRaises(DataError):
            normalize({'resources': [resource()], 'weights': {'authority': -1}})

    def test_large_finite_weights_do_not_overflow(self):
        result = rank_resources({'resources': [resource()], 'weights': dict.fromkeys(DEFAULT_WEIGHTS, 1e308)})
        self.assertEqual(result['resources'][0]['total_score'], 80)
        self.assertTrue(all(math.isfinite(v) for v in result['weights'].values()))

    def test_enormous_integer_weight_has_readable_error(self):
        with self.assertRaises(DataError):
            normalize({'resources': [resource()], 'weights': {'authority': 10**1000}})

    def test_unknown_weight_is_rejected(self):
        with self.assertRaises(DataError):
            normalize({'resources': [resource()], 'weights': {'relevence': 1}})

    def test_missing_score_is_rejected(self):
        item = resource()
        del item['scores']['currency']
        with self.assertRaises(DataError):
            rank_resources([item])

    def test_unknown_score_is_rejected(self):
        item = resource(); item['scores']['curreny'] = 4
        with self.assertRaises(DataError):
            rank_resources([item])

    def test_out_of_range_score_is_rejected(self):
        for value in [-.01, 5.01]:
            with self.subTest(value=value), self.assertRaises(DataError):
                rank_resources([resource(score=value)])

    def test_bad_names_are_rejected(self):
        for name in ['', '  ', None, 4]:
            with self.subTest(name=name), self.assertRaises(DataError):
                rank_resources([resource(name=name)])

    def test_empty_resources_and_bad_top_levels_are_rejected(self):
        for payload in [[], {'resources': []}, {'resources': {}}, None, 5, 'a']:
            with self.subTest(payload=payload), self.assertRaises(DataError):
                rank_resources(payload)

    def test_ties_preserve_input_order(self):
        out = rank_resources([resource('first'), resource('second')])
        self.assertEqual([r['name'] for r in out['resources']], ['first', 'second'])

    def test_rank_uses_unrounded_scores(self):
        a = resource('a'); b = resource('b')
        a['scores']['authority'] = 4.001
        b['scores']['authority'] = 4.002
        result = rank_resources([a, b])['resources']
        self.assertEqual(result[0]['total_score'], result[1]['total_score'])
        self.assertEqual(result[0]['name'], 'b')

    def test_inputs_are_not_mutated(self):
        source = {'resources': [resource()], 'weights': {'authority': 2}}
        before = copy.deepcopy(source)
        rank_resources(source)
        self.assertEqual(source, before)

    def test_markdown_escapes_html_pipe_and_newline(self):
        out = render_markdown([{'name': '<x>|\ny', 'total_score': 80}])
        self.assertIn('&lt;x&gt;\\|<br>y', out)
        self.assertEqual(len(out.splitlines()), 3)

    def test_random_valid_scores_stay_in_range(self):
        rng = random.Random(17)
        for _ in range(100):
            item = resource(); item['scores'] = {key: rng.uniform(0, 5) for key in DEFAULT_WEIGHTS}
            out = rank_resources([item])['resources'][0]['total_score']
            self.assertLessEqual(out, 100); self.assertGreaterEqual(out, 0)

    def test_cli_json_runs_from_different_working_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(ROOT/'scripts/score_resources.py'),
                                     str(ROOT/'examples/resources.example.json'), '--json'],
                                    cwd=temp, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['resources'][0]['total_score'], 90)

    def test_cli_invalid_input_exits_two_without_traceback(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'bad.json'; path.write_text('{bad}', encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT/'scripts/score_resources.py'), str(path)],
                                    capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 2)
        self.assertIn('ERROR:', result.stderr)
        self.assertNotIn('Traceback', result.stderr)


class StrictJsonTests(unittest.TestCase):
    def read_bytes(self, data):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'input.json'; path.write_bytes(data)
            return load_json(path)

    def test_accepts_utf8_bom_and_chinese(self):
        self.assertEqual(self.read_bytes('\ufeff{"名称":"课程"}'.encode('utf-8')), {'名称': '课程'})

    def test_rejects_duplicate_keys(self):
        with self.assertRaisesRegex(DataError, 'duplicate'):
            self.read_bytes(b'{"a":1,"a":2}')

    def test_rejects_nonstandard_numeric_constants(self):
        for value in [b'NaN', b'Infinity', b'-Infinity']:
            with self.subTest(value=value), self.assertRaises(DataError):
                self.read_bytes(b'{"a":'+value+b'}')

    def test_rejects_float_overflow_literal(self):
        with self.assertRaises(DataError):
            self.read_bytes(b'{"a":1e999}')

    def test_rejects_invalid_encoding(self):
        with self.assertRaises(DataError):
            self.read_bytes(bytes([255, 254]))

    def test_missing_file_is_readable_error(self):
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(DataError):
            load_json(Path(temp)/'absent.json')

    def test_directory_is_readable_error(self):
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(DataError):
            load_json(Path(temp))

    def test_numeric_string_is_not_silently_coerced(self):
        with self.assertRaises(DataError):
            number('3', 'test')


if __name__ == '__main__':
    unittest.main()
