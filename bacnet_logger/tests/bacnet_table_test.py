import pytest
from ..bacnet_table import (_parse_obj_name, BacnetObject)

def test_parse_obj_name():
    obj_names = {
        'Lab1115_HVACModeStatus': ['zone', 1, 'Lab1115', 'HVACModeStatus'],
        'Lab1115_RmTmp': ['zone', 1, 'Lab1115', 'RmTmp'],
        'Lab1115_TotalEaFl': ['zone', 1, 'Lab1115', 'EaFl'],
        'Lab1115_TotalSaFl': ['zone', 1, 'Lab1115', 'SaFl'],
        'SAV1100A_HVACModeStatus': ['zone', 1, 'SAV1100A', 'HVACModeStatus'],
        'Lab_2311_EaFl': ['zone', 2, 'Lab_2311', 'EaFl'],
        'Lab-2200_EaFl': ['zone', 2, 'Lab-2200', 'EaFl'],
        'VAV-2-101_AirFl': ['zone', 1, 'VAV-2-101', 'SaFl'],
        'VAV-4-314_CO2': ['zone', 3, 'VAV-4-314', 'CO2'],
        'CalcNPWTotal_gal': ['water', -99, 'CalcNPWTotal_gal', 'NPW'],
        'CalcDomChwTotal_gal': ['water', -99, 'CalcDomChwTotal_gal', 'ChW'],
        'NPWIrrigationMtr_gal': ['water', -99, 'NPWIrrigationMtr_gal', 'NPW'],
        'El_SubMtr_A1NLH1_WH': ['power', -99, 'El_SubMtr_A1NLH1', 'wh'],
        'El_SubMtr_B1ELH2_B3ELH1_WH': ['power', -99, 'El_SubMtr_B1ELH2_B3ELH1', 'wh'],
        'Service_Transformer1_Kwh': ['power', -99, 'Service_Transformer1', 'kwh'],
    }
    for obj_name, results in obj_names.items():
        print(f"{results=}")
        (category, floor, identifier, attribute) = _parse_obj_name(obj_name)
        if category != results[0]:
            assert False, f"{obj_name} {category=} incorrect."
        if int(floor) != results[1]:
            assert False, f"{obj_name} {floor=} incorrect."
        if identifier != results[2]:
            assert False, f"{obj_name} {identifier=} incorrect."
        if attribute != results[3]:
            assert False, f"{obj_name} {attribute=} incorrect."
    assert True

@pytest.fixture
def sample_bacnet_objects():
    return [
        {
            'obj_type': 'multiStateValue',
            'obj_id': '4',
            'obj_name': 'Lab1115_HVACModeStatus'
        },
        {
            'obj_type': 'analogValue',
            'obj_id': '19',
            'obj_name': 'Lab1115_RmTmp'
        },
    ]

def test_bacnet_object(sample_bacnet_objects):
    objm = sample_bacnet_objects[0]
    mo = BacnetObject(objm['obj_type'], int(objm['obj_id']), objm['obj_name'])
    assert int(mo.floor) == 1
