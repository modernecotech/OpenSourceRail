"""Bench-only administrative probes. No staffing or work-release writes."""
import hashlib
import time

SNAPSHOTS={
    'evidence_tasks':("tabTask", "JSON_ARRAY(name,subject,status,COALESCE(project,''),description)", " WHERE subject LIKE 'BAG-EVID-%'"),
    'doctype_schema':('tabDocType','JSON_ARRAY(name,module,modified)',''),
    'role_membership':('tabHas Role','JSON_ARRAY(name,parent,parenttype,role)',''),
    'doctype_permissions':('tabDocPerm','JSON_ARRAY(name,parent,role,`read`,`write`,`create`,`submit`,`cancel`,`amend`)',''),
    'user_permissions':('tabUser Permission','JSON_ARRAY(name,user,allow,for_value)',''),
    'private_file_inventory':('tabFile','JSON_ARRAY(name,file_url,is_private,file_size,content_hash)',''),
}

def snapshot_queries():
    return {key:f"SELECT SHA2({expression},256) FROM `{table}`{where} ORDER BY name" for key,(table,expression,where) in SNAPSHOTS.items()}

def _require_manager():
    import frappe
    if 'System Manager' not in frappe.get_roles():frappe.throw('System Manager required for local administrative probe')
    return frappe

def recovery_fingerprint():
    """Compare hashes, not personal records/secrets, against an isolated restore."""
    frappe=_require_manager();result={}
    for key,query in snapshot_queries().items():
        rows=frappe.db.sql(query)
        result[key]=dict(count=len(rows),sha256=hashlib.sha256(''.join(str(r[0])+'\n' for r in rows).encode()).hexdigest())
    return dict(records=result,read_only=True,operational_release=False,appointments_verified=False)

def read_probe(repetitions=5):
    """Bounded native reads; permission-aware samples and actual elapsed time."""
    frappe=_require_manager()
    if isinstance(repetitions,bool) or not isinstance(repetitions,int) or not 1<=repetitions<=30:
        raise ValueError('Use 1 to 30 repetitions')
    from osr_erpnext.workforce import administration_readiness
    readiness=administration_readiness();samples=[]
    for _ in range(repetitions):
        start=time.monotonic();read=0
        for row in readiness['record_types']:
            if row['schema_exists'] and row['caller_can_read']:
                read+=len(frappe.get_list(row['doctype'],fields=['name'],limit_page_length=50))
        samples.append(dict(seconds=time.monotonic()-start,permission_filtered_rows_read=read))
    return dict(readiness=readiness,samples=samples,maximum_sample_rows_per_type=50,
        proof_of_city_scale=False,read_only=True,operational_release=False)
