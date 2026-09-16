"""Native integration references; no upstream patches."""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def install():
    fields = {}
    for dt in ['Asset', 'Item', 'BOM', 'Purchase Order Item', 'Purchase Receipt Item', 'Work Order', 'Issue']:
        fields[dt] = [dict(fieldname='custom_osr_asset_id', label='OSR planned asset', fieldtype='Data'),
                      dict(fieldname='custom_osr_component_type', label='OSR component type', fieldtype='Data'),
                      dict(fieldname='custom_osr_design_revision', label='OSR design revision', fieldtype='Data')]
    fields['Issue'] += [dict(fieldname='custom_osr_' + name, label=label, fieldtype=kind, **extras)
        for name, label, kind, extras in [
            ('incident_key', 'OSR incident identity', 'Data', {'unique': 1, 'read_only': 1}),
            ('environment', 'OSR environment', 'Data', {'read_only': 1}),
            ('city', 'OSR city', 'Data', {'read_only': 1}),
            ('erp_asset', 'OSR ERP Asset', 'Link', {'options': 'Asset'}),
            ('condition', 'OSR observed condition', 'Data', {'read_only': 1}),
            ('condition_history', 'OSR condition events', 'Code', {'options': 'JSON', 'read_only': 1}),
            ('evidence_path', 'OSR evidence and trends', 'Data', {'read_only': 1})]]
    fields['Asset Repair'] = [dict(fieldname='custom_osr_' + name, label=label, fieldtype=kind,
        no_copy=1, **extras) for name, label, kind, extras in [
            ('repair_key', 'OSR repair identity', 'Data', {'unique': 1, 'read_only': 1}),
            ('repair_sha256', 'OSR reviewed repair checksum', 'Data', {'read_only': 1}),
            ('repair_request', 'OSR reviewed repair request', 'Code', {'options': 'JSON', 'read_only': 1}),
            ('issue', 'Originating OSR Issue', 'Link', {'options': 'Issue', 'read_only': 1}),
            ('environment', 'OSR environment', 'Data', {'read_only': 1}),
            ('city', 'OSR city', 'Data', {'read_only': 1}),
            ('asset_id', 'OSR railway asset ID', 'Data', {'read_only': 1}),
            ('expected_downtime_hours', 'Expected downtime (hours)', 'Float', {}),
            ('configuration_evidence', 'OSR condition and configuration evidence', 'Code',
                {'options': 'JSON', 'read_only': 1}),
            ('handback_required', 'Independent railway handback required', 'Check',
                {'default': '1', 'read_only': 1}),
        ]]
    create_custom_fields(fields)
    if not frappe.db.exists('DocType', 'OSR Execution Mapping'):
        frappe.get_doc(dict(doctype='DocType', name='OSR Execution Mapping', module='OpenSourceRail', custom=1,
            autoname='field:mapping_key', track_changes=1,
            fields=[dict(fieldname=name, label=label, fieldtype=kind, reqd=1, **options) for name, label, kind, options in [
                ('mapping_key', 'Mapping identity', 'Data', {'unique': 1}),
                ('company', 'Company', 'Link', {'options': 'Company'}),
                ('city', 'City', 'Data', {}),
                ('component_type', 'Component type', 'Data', {}),
                ('engineering_revision', 'Engineering revision', 'Data', {}),
                ('engineering_sha256', 'Engineering package checksum', 'Data', {}),
                ('erp_item', 'Item', 'Link', {'options': 'Item'}),
                ('source_package', 'Reviewed conversion package', 'Code', {'options': 'JSON'}),
            ]], permissions=[dict(role='Manufacturing Manager', read=1, write=1, create=1),
                             dict(role='Projects Manager', read=1), dict(role='System Manager', read=1, write=1, create=1)])).insert()
