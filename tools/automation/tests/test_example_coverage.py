"""Coverage must not turn missing evidence or a changed contract into a green result."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'deployment/erpnext/apps/osr_erpnext'))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
coverage=module('example_coverage_tests','deployment/example-city/coverage.py')
contracts=module('example_contract_tests','deployment/example-city/contracts.py')


class CoverageTest(unittest.TestCase):
    def setUp(self):
        self.rows=[dict(id='component.amount',source='schema.py',kind='input',options=['Stop','Warn'])]
        self.plan=dict(scope='fixture',reviewed_ids=['component.amount'],reviewed_contracts={r['id']:coverage.signature(r) for r in self.rows},
            rules=[dict(pattern='component.amount',status='varied',remaining='Other combinations remain',evidence=[dict(report='expansion',check='amount.*')])])
        self.reports=dict(expansion=dict(passed=True,checks=[dict(id='amount.small',passed=True)]))

    def test_current_inventory_is_reviewed_and_rules_match(self):
        rows=coverage.inventory(ROOT);plan=json.loads((ROOT/'deployment/example-city/coverage-plan.json').read_text())
        result=coverage.assess(rows,plan,{})
        self.assertTrue(result['inventory_consistent'],result['drift'])
        self.assertEqual(result['counts'],{'gap':len(rows)})
        self.assertFalse(result['exhaustive'])
        for required in ['erp.input.budget.accounts[].amount','fuxa.project','controller.crossing_motor_fault','workflow.backup-restore']:
            self.assertIn(required,{r['id'] for r in rows})

    def test_passed_run_and_matching_check_required(self):
        self.assertEqual(coverage.assess(self.rows,self.plan,self.reports)['counts'],{'varied':1})
        for report in [{},dict(passed=False,checks=[dict(id='amount.small',passed=True)]),dict(passed=None,checks=[dict(id='amount.small',passed=True)]),dict(passed=True,checks=[dict(id='amount.small',passed=False)]),dict(passed=True,checks=[dict(id='unrelated',passed=True)])]:
            with self.subTest(report=report):self.assertEqual(coverage.assess(self.rows,self.plan,{'expansion':report})['counts'],{'gap':1})

    def test_new_removed_and_changed_contracts_are_detected(self):
        changed=copy.deepcopy(self.rows);changed[0]['options'].append('Ignore')
        result=coverage.assess(changed,self.plan,self.reports)
        self.assertFalse(result['inventory_consistent']);self.assertEqual(result['drift']['changed'],['component.amount']);self.assertEqual(result['counts'],{'gap':1})
        result=coverage.assess(self.rows+[dict(id='new',kind='input')],self.plan,self.reports)
        self.assertEqual(result['drift']['added'],['new'])
        result=coverage.assess([],self.plan,self.reports)
        self.assertEqual(result['drift']['removed'],['component.amount']);self.assertEqual(result['unused_rules'],['component.amount'])

    def test_registered_schema_matrix_has_unique_checks_for_every_input(self):
        with tempfile.TemporaryDirectory() as folder:
            class Harness:
                OUTPUT=Path(folder)
                @staticmethod
                def write(path,value):path.write_text(json.dumps(value))
            report=contracts.verify(Harness)
        self.assertTrue(report['passed']);self.assertFalse(report['exhaustive'])
        ids={r['id'] for r in report['checks']}
        self.assertEqual(len(ids),len(report['checks']))
        for row in coverage.inventory(ROOT):
            if row['id'].startswith('erp.input.'):
                self.assertIn('contract.'+row['id']+'.missing',ids)
        self.assertEqual({r['level'] for r in report['checks']},{'schema-only'})

if __name__=='__main__':unittest.main()
