"""Curriculum consistency checks; no web or model calls."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts._common import DataError, load_json
from scripts.validate_plan import validate_plan

BASE = ROOT / 'examples/python-testing'


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.plan = load_json(BASE/'plan.json')
        self.ledger = load_json(BASE/'resources.json')

    def check(self):
        return validate_plan(self.plan, self.ledger, BASE)

    def test_complete_plan_is_valid(self):
        result = self.check()
        self.assertEqual(result['covered_required_capabilities'], 3)
        self.assertEqual(result['hours']['total'], 4)
        self.assertEqual(result['warnings'], [])

    def test_budget_includes_buffer(self):
        self.plan['buffer_hours'] = .6
        with self.assertRaisesRegex(DataError, 'exceed budget'):
            self.check()

    def test_negative_hours_rejected(self):
        self.plan['lessons'][0]['hours']['practice'] = -1
        with self.assertRaises(DataError): self.check()

    def test_boolean_budget_rejected(self):
        self.plan['budget_hours'] = True
        with self.assertRaises(DataError): self.check()

    def test_nonfinite_hours_rejected(self):
        self.plan['lessons'][0]['hours']['input'] = float('inf')
        with self.assertRaises(DataError): self.check()

    def test_zero_time_lesson_rejected(self):
        self.plan['lessons'][0]['hours'] = dict.fromkeys(['input','practice','assessment'], 0)
        with self.assertRaisesRegex(DataError, 'positive total'):
            self.check()

    def test_unknown_dependency_rejected(self):
        self.plan['capabilities'][1]['requires'] = ['missing']
        with self.assertRaisesRegex(DataError, 'unknown prerequisite'):
            self.check()

    def test_dependency_cycle_rejected(self):
        self.plan['capabilities'][0]['requires'] = ['c-isolation']
        with self.assertRaisesRegex(DataError, 'cycle'):
            self.check()

    def test_out_of_order_lessons_rejected(self):
        self.plan['lessons'][0], self.plan['lessons'][1] = self.plan['lessons'][1], self.plan['lessons'][0]
        with self.assertRaisesRegex(DataError, 'not learned yet'):
            self.check()

    def test_known_capability_can_be_skipped(self):
        self.plan['known_capabilities'].append('c-test')
        self.plan['lessons'].pop(0)
        self.assertTrue(self.check()['valid'])

    def test_unknown_known_capability_rejected(self):
        self.plan['known_capabilities'].append('invented')
        with self.assertRaisesRegex(DataError, 'unknown known'):
            self.check()

    def test_missing_required_capability_rejected(self):
        self.plan['capabilities'].append({'id':'missing','title':'not covered','requires':[],'required':True})
        with self.assertRaisesRegex(DataError, 'not covered'):
            self.check()

    def test_unknown_selected_resource_rejected(self):
        self.plan['selected_resource_ids'].append('missing')
        with self.assertRaisesRegex(DataError, 'unknown selected'):
            self.check()

    def test_unused_selected_resource_rejected(self):
        extra = copy.deepcopy(self.ledger['resources'][0]); extra['id'] = 'unused'
        extra['role'] = 'optional'
        self.ledger['resources'].append(extra)
        self.plan['selected_resource_ids'].append('unused')
        with self.assertRaisesRegex(DataError, 'unused'):
            self.check()

    def test_skipped_resource_cannot_be_selected(self):
        self.ledger['resources'][0]['role'] = 'skip'
        with self.assertRaisesRegex(DataError, 'marked skip'):
            self.check()

    def test_core_resource_limit_enforced(self):
        self.plan['max_core_resources'] = 1
        with self.assertRaisesRegex(DataError, 'max_core_resources'):
            self.check()

    def test_boolean_resource_limit_rejected(self):
        self.plan['max_core_resources'] = True
        with self.assertRaises(DataError): self.check()

    def test_no_declared_coverage_rejected(self):
        for r in self.ledger['resources']:
            r['covers'] = []
        with self.assertRaisesRegex(DataError, 'no referenced resource'):
            self.check()

    def test_unverified_resource_cannot_support_verified_plan(self):
        self.ledger['resources'][0]['verification'] = {'status':'unverified','checked_at':None,'evidence':''}
        with self.assertRaisesRegex(DataError, 'unverified/metadata-only'):
            self.check()

    def test_metadata_only_cannot_support_verified_plan(self):
        self.ledger['resources'][0]['verification']['status'] = 'metadata-only'
        with self.assertRaises(DataError): self.check()

    def test_offline_provisional_resource_is_labeled(self):
        self.plan['mode'] = 'offline'
        self.ledger['resources'][0]['verification'] = {'status':'unverified','checked_at':None,'evidence':''}
        result = self.check()
        self.assertTrue(any('Provisional selected resource' in x for x in result['warnings']))

    def test_claimed_verification_needs_evidence(self):
        self.ledger['resources'][0]['verification']['evidence'] = ''
        with self.assertRaises(DataError): self.check()

    def test_future_check_date_rejected(self):
        self.ledger['resources'][0]['verification']['checked_at'] = '9999-12-31'
        with self.assertRaisesRegex(DataError, 'future'):
            self.check()

    def test_invalid_calendar_date_rejected(self):
        self.ledger['resources'][0]['verification']['checked_at'] = '2026-02-30'
        with self.assertRaisesRegex(DataError, 'calendar date'):
            self.check()

    def test_missing_section_rejected(self):
        self.plan['lessons'][0]['section_refs'][0]['section_id'] = 'invented'
        with self.assertRaisesRegex(DataError, 'unknown section'):
            self.check()

    def test_unverified_section_rejected(self):
        self.ledger['resources'][0]['sections'][0]['verified'] = False
        with self.assertRaisesRegex(DataError, 'unverified section'):
            self.check()

    def test_duplicate_section_reference_rejected(self):
        refs = self.plan['lessons'][0]['section_refs']; refs.append(copy.deepcopy(refs[0]))
        with self.assertRaisesRegex(DataError, 'duplicate section reference'):
            self.check()

    def test_duplicate_resource_id_rejected(self):
        self.ledger['resources'].append(copy.deepcopy(self.ledger['resources'][0]))
        with self.assertRaisesRegex(DataError, 'duplicate resource'):
            self.check()

    def test_duplicate_capability_id_rejected(self):
        self.plan['capabilities'].append(copy.deepcopy(self.plan['capabilities'][0]))
        with self.assertRaisesRegex(DataError, 'duplicate capability'):
            self.check()

    def test_duplicate_lesson_id_rejected(self):
        self.plan['lessons'][1]['id'] = self.plan['lessons'][0]['id']
        with self.assertRaisesRegex(DataError, 'duplicate lesson'):
            self.check()

    def test_empty_mastery_gate_rejected(self):
        self.plan['lessons'][0]['exit_criteria'] = []
        with self.assertRaises(DataError): self.check()

    def test_local_path_traversal_rejected(self):
        self.ledger['resources'][2]['url'] = 'repo:../private.txt'
        with self.assertRaisesRegex(DataError, 'traversal'):
            self.check()

    def test_absolute_windows_path_rejected(self):
        self.ledger['resources'][2]['url'] = 'repo:C:\\private.txt'
        with self.assertRaisesRegex(DataError, 'relative POSIX'):
            self.check()

    def test_missing_local_file_rejected(self):
        self.ledger['resources'][2]['url'] = 'repo:lab/missing.py'
        with self.assertRaisesRegex(DataError, 'file not found'):
            self.check()

    def test_http_credentials_rejected(self):
        self.ledger['resources'][0]['url'] = 'https://token@docs.python.org/page'
        with self.assertRaisesRegex(DataError, 'without credentials'):
            self.check()

    def test_local_evidence_cannot_impersonate_remote(self):
        self.ledger['resources'][0]['verification']['status'] = 'local'
        with self.assertRaisesRegex(DataError, 'local verification'):
            self.check()

    def test_no_independent_work_produces_warning(self):
        for lesson in self.plan['lessons']: lesson['kind'] = 'guided'
        self.assertTrue(any('independent/transfer' in w for w in self.check()['warnings']))

    def test_no_practice_produces_warning(self):
        for lesson in self.plan['lessons']: lesson['hours']['practice'] = 0
        self.assertTrue(any('No practice' in w for w in self.check()['warnings']))

    def test_unknown_top_level_field_rejected(self):
        self.plan['buget_hours'] = 4
        with self.assertRaisesRegex(DataError, 'unknown fields'):
            self.check()

    def test_no_mutation(self):
        plan_before = copy.deepcopy(self.plan); ledger_before = copy.deepcopy(self.ledger)
        self.check()
        self.assertEqual(self.plan, plan_before); self.assertEqual(self.ledger, ledger_before)

    def test_cli_valid_from_another_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(ROOT/'scripts/validate_plan.py'),
                str(BASE/'plan.json'), '--resources', str(BASE/'resources.json'), '--json'],
                cwd=temp, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['valid'])

    def test_cli_error_json_returns_two(self):
        with tempfile.TemporaryDirectory() as temp:
            bad = Path(temp)/'bad.json'; bad.write_text('{}',encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT/'scripts/validate_plan.py'),
                str(bad), '--resources', str(BASE/'resources.json'), '--json'],
                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)['valid'])
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
