from pathlib import Path
from clinic import Clinic, ClinicError
from import_patients import import_csv
import pytest

CSV = Path(__file__).resolve().parents[1] / 'sample_patients.csv'

def test_sample_records_and_saved_history(tmp_path):
    path = str(tmp_path / 'clinic.json')
    clinic = Clinic(path)
    report = import_csv(clinic, CSV)
    assert len(report['imported']) == 15 and not report['invalid']
    p = clinic.find_patients('Juan Dela Cruz')[0]
    assert p.category == 'Senior'
    q = clinic.find_patients('Lourdes')[0]
    clinic.add_to_queue(p.patient_id, 'routine')
    clinic.add_to_queue(q.patient_id, 'urgent')
    assert clinic.serve_next()[0] is q
    clinic.add_benefit_request(q.patient_id, 'Cane')
    clinic.approve_benefits('5000', 'dp')
    clinic.add_home_visit(q.patient_id, '09:00', '10:00')
    reloaded = Clinic(path)
    assert reloaded.patient_count == 15
    found = reloaded.find_by_id(q.patient_id)
    assert len(found.visits) == 1 and found.claims[0]['item'] == 'Cane'
    assert reloaded.plan_home_visits()['chosen'][0]['patient'] is found
    assert reloaded.waiting_list()[0]['patient'].patient_id == p.patient_id
    with pytest.raises(ClinicError):
        reloaded.add_benefit_request(found.patient_id,'Cane')

def test_category_counts():
    clinic = Clinic()
    import_csv(clinic, CSV, save=False)
    assert {c:sum(p.category==c for p in clinic.patients) for c in ('Senior','PWD','Senior and PWD')} == {'Senior':7,'PWD':5,'Senior and PWD':3}

def test_bundled_database_and_recovery(tmp_path):
    import shutil
    bundled = CSV.parent / 'data' / 'clinic_data.json'
    copy = tmp_path / 'clinic.json'
    shutil.copyfile(bundled, copy)
    c = Clinic(str(copy))
    assert c.patient_count == 15
    assert c.find_patients('Juan Dela Cruz')[0].patient_id == 'P-0001'
    assert all(len(p.visits) == 0 for p in c.patients)
    report = import_csv(c, CSV)
    assert len(report['duplicates']) == 15 and not report['imported']
    empty = Clinic(str(tmp_path / 'empty.json'))
    empty.save()
    assert Clinic(empty.path).patient_count == 0
    assert len(import_csv(empty, CSV)['imported']) == 15
    assert Clinic(empty.path).patient_count == 15
