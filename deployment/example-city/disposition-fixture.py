"""Seed retained browser-only test work and distinct users in the isolated example."""
import os,json
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site=INPUT['site']);frappe.connect();frappe.flags.mute_emails=True
try:
    from osr_erpnext.components import preview,apply
    source=INPUT['source'];roles=['Projects Manager','Manufacturing Manager','Manufacturing User','Purchase Manager','Stock Manager','Stock User','Quality Manager']
    users={}
    for role,password in INPUT['passwords'].items():
        email='osr-browser-'+role+'-'+INPUT['run']+'@example.invalid'
        doc=frappe.get_doc(dict(doctype='User',email=email,first_name='Browser '+role,enabled=1,send_welcome_email=0,new_password=password,user_type='System User',roles=[dict(role=r) for r in roles])).insert()
        frappe.share.add('Project',source['project'],email,read=1,write=1,notify=0);users[role]=email
    values=dict(bom=source['bom'],quantity=2,source_warehouse=source['warehouse'],wip_warehouse=source['warehouse'],fg_warehouse=source['warehouse'],start=frappe.utils.now_datetime().strftime('%Y-%m-%d %H:%M:%S'))
    plan=preview(source['project'],'manufacturing','browser-'+INPUT['run'],values)
    result=apply(source['project'],'manufacturing','browser-'+INPUT['run'],values,plan['fingerprint'])
    order=frappe.get_doc('Work Order',result['name']);order.skip_transfer=1;order.save();order.submit()
    from osr_erpnext.disposition import catalogue
    mapping=next(r['mapping']['name'] for r in catalogue(source['project'])['reviews'] if any(t['target']['document']==order.name for t in r['targets']))
    frappe.db.commit()
    print('OSR_FIXTURE:'+json.dumps(dict(users=users,project=source['project'],order=order.name,mapping=mapping)),flush=True)
except BaseException:frappe.db.rollback();raise
finally:frappe.destroy()
