"""Run with Flask installed. Uses isolated data, never the user's saved records."""
import pytest
pytest.importorskip('flask')
from app import create_app
from import_patients import import_csv
from pathlib import Path

def test_patient_workflow(tmp_path):
    app = create_app(str(tmp_path/'test.json'))
    app.config['TESTING'] = True
    clinic = app.extensions['clinic']
    import_csv(clinic, Path(__file__).resolve().parents[1]/'sample_patients.csv')
    client = app.test_client()
    for page in ('/','/patients','/register','/queue','/schedule','/benefits'):
        assert client.get(page).status_code == 200
    assert client.get('/analysis').status_code == 404
    response = client.get('/patients?q=Juan+Dela+Cruz')
    assert b'Juan Dela Cruz' in response.data and b'Maria Santos' not in response.data
    response = client.get('/patients?category=PWD')
    assert b'Ben Reyes' in response.data and b'Juan Dela Cruz' not in response.data
    p = clinic.find_patients('Juan')[0]
    pid = p.patient_id
    assert client.post('/queue/add', data={'patient_id':pid,'condition':'routine'}).status_code == 302
    assert client.post('/queue/serve').status_code == 302
    assert client.post('/benefits/add',data={'patient_id':pid,'item':'Cane'}).status_code == 302
    assert client.post('/benefits/approve',data={'budget':'5000'}).status_code == 302
    assert client.post('/schedule/add',data={'patient_id':pid,'start':'09:00','end':'10:00'}).status_code == 302
    result = client.get('/patient/'+pid)
    assert result.status_code == 200
    for text in (b'Juan Dela Cruz', b'Clinic Visit History', b'09:00', b'Cane', b'Served'):
        assert text in result.data

def test_recover_empty_database(tmp_path):
    from clinic import Clinic
    path = str(tmp_path / 'empty.json')
    Clinic(path).save()
    app = create_app(path)
    client = app.test_client()
    assert b'Load 15 Sample Patients' in client.get('/patients').data
    assert client.post('/demo/import', follow_redirects=True).status_code == 200
    assert app.extensions['clinic'].patient_count == 15
    client.post('/demo/import')
    assert app.extensions['clinic'].patient_count == 15
