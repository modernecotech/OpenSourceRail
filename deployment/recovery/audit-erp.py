"""Native read-only record/encryption audit for an isolated recovery clone."""
import os,json,hashlib
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site=os.environ.get('OSR_RESTORE_SITE','osr.localhost'));frappe.connect()
try:
 fields={'Issue':['project','status','custom_osr_incident_key','custom_osr_condition_history','custom_osr_asset_id','custom_osr_city'],'GL Entry':['company','account','voucher_type','voucher_no','debit','credit','project','is_cancelled'],'Stock Ledger Entry':['company','item_code','warehouse','voucher_type','voucher_no','actual_qty','qty_after_transaction','stock_value_difference'],'File':['file_name','file_url','is_private','file_size','content_hash'],'Project':['project_name','company','status','percent_complete'],'Task':['project','subject','status','progress','exp_start_date','exp_end_date'],'Asset':['asset_name','company','item_code','gross_purchase_amount'],'Serial No':['item_code','warehouse','status'],'Work Order':['production_item','bom_no','qty','produced_qty','status'],'Purchase Invoice':['company','supplier','grand_total','outstanding_amount','docstatus'],'Material Request':['company','material_request_type','status','docstatus'],'Stock Entry':['company','stock_entry_type','docstatus']}
 records={}
 for dt,wanted in fields.items():
  meta=frappe.get_meta(dt);selected=['name']+[f for f in wanted if f=='docstatus' or meta.has_field(f)]
  rows=frappe.get_all(dt,fields=selected,order_by='name asc',limit_page_length=0)
  records[dt]={'count':len(rows),'fields':selected,'sha256':hashlib.sha256(json.dumps(rows,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()}
 from frappe.utils.password import get_decrypted_password
 secrets=frappe.db.sql('select doctype,name,fieldname from __Auth where encrypted=1',as_dict=True)
 for row in secrets:assert get_decrypted_password(row.doctype,row.name,row.fieldname,raise_exception=True) is not None
 print(json.dumps({'records':records,'encrypted_fields_readable':len(secrets)},indent=2))
finally:frappe.db.rollback();frappe.destroy()
