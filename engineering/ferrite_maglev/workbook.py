"""Bounded OOXML input reader. Spreadsheet formulas are never executed here."""
from hashlib import sha256
from xml.etree import ElementTree as ET
from zipfile import ZipFile

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
FIXED = ('cars direct_usd labour_hours labour_usd_h premium reference_train_tare_kg '
         'aw2_passengers aw3_passengers passenger_kg ferrite_usd_kg battery_kwh_train '
         'battery_pack_usd_train pack_wh_kg base_tare_kg base_ferrite_kg base_battery_kwh '
         'gravity_m_s2 soc_window eol_fraction modules_car remove_bogies_usd remove_motors_usd '
         'remove_gears_usd remove_drives_usd remove_cooling_usd elevated_usd_km '
         'rail_supply_usd_km beam_m_km supplied_components_usd_km old_brackets_usd_km '
         'erection_usd_km transport_usd_km temporary_usd_km installation_usd_km '
         'night_usd_km qa_usd_km relocation_usd_km traffic_usd_km supports_usd_km fte_usd_year').split()
SCENARIO = ('iron_carriers_usd windings_usd drives_usd sensing_usd cooling_usd finished_array_usd '
            'capture_usd integration_hours structure_factor rail_supply_usd_km brackets_usd_km '
            'erection_factor transport_factor temporary_factor installation_factor night_factor '
            'qa_factor relocation_factor traffic_factor supports_factor engineering_fte_years '
            'independent_testing_usd rigs_usd fixtures_usd first_article_usd pilot_guideway_usd '
            'site_power_recovery_usd pilot_reserve').split()


def read(path):
    """Import revision-A literal input cells, preserving their addresses and source hash."""
    import math
    with ZipFile(path) as archive:
        if sum(i.file_size for i in archive.infolist()) > 16 * 1024 * 1024:
            raise ValueError('workbook exceeds bounded import size')
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        names = [s.get('name') for s in workbook.find('s:sheets', NS)]
        if names != ['Comparison', 'Vehicle', 'Civil', 'Inputs', 'Pilot']:
            raise ValueError('unsupported workbook layout')
        # Resolve worksheet relationships instead of relying on ZIP member order.
        rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
                if r.get('TargetMode') != 'External'}
        sheet = list(workbook.find('s:sheets', NS))[3]
        target = rels[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
        import posixpath
        target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        if not target.startswith('xl/worksheets/') or '..' in target.split('/'):
            raise ValueError('invalid worksheet relationship')
        cells = {c.get('r'): c for c in ET.fromstring(archive.read(target)).findall('s:sheetData/s:row/s:c', NS)}
    result = dict(schema='osr-maglev-cost-inputs/1', workbook_sha256=sha256(path.read_bytes()).hexdigest(),
                  fixed={}, scenarios={}, cells={}, evidence='supplied unquoted planning allowances')

    def number(address):
        cell = cells[address]
        if cell.find('s:f', NS) is not None or cell.get('t', 'n') != 'n':
            raise ValueError('literal numeric input required: ' + address)
        value = float(cell.find('s:v', NS).text)
        if not math.isfinite(value) or value < 0:
            raise ValueError('finite nonnegative input required: ' + address)
        return value

    for row, name in enumerate(FIXED, 16):
        result['fixed'][name] = number('C' + str(row))
        result['cells']['fixed/' + name] = 'Inputs!C' + str(row)
    for scenario, col in [('low', 'C'), ('base', 'D'), ('high', 'E')]:
        result['scenarios'][scenario] = {}
        for row, name in enumerate(SCENARIO, 59):
            result['scenarios'][scenario][name] = number(col + str(row))
            result['cells'][scenario + '/' + name] = 'Inputs!' + col + str(row)
    return result
