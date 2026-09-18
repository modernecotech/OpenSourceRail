frappe.ui.form.on("Project", {
  refresh(frm) {
    if (!frm.doc.custom_osr_city || frm.is_new()) return;
    frm.add_custom_button(__('Revision dispositions'), () => osr_revision_dispositions(frm), __('OpenSourceRail'));
    frm.add_custom_button(__("Connected lifecycle"), () => {
      osr_open_lifecycle({city:frm.doc.custom_osr_city});
    }, __('OpenSourceRail'));
    frm.add_custom_button(__("Operating twin"), () => {
      frappe.call({
        type: "GET",
        method: "osr_erpnext.city_runtime.city_status",
        args: { project: frm.doc.name },
        callback({ message: twin }) {
          const escape = frappe.utils.escape_html;
          const rows = Object.entries(twin.categories).map(([kind, statuses]) =>
            `<tr><td>${escape(kind)}</td><td>${escape(Object.entries(statuses).map(([k, v]) => `${k}: ${v}`).join(" · "))}</td></tr>`
          ).join("");
          frappe.msgprint({ title: __("City operating twin"), wide: true,
            message: `<p><b>${escape(twin.city)}</b> · ${escape(twin.engineering_revision)} · operating release ${escape(twin.operating_release)}</p>` +
              `<table class="table"><thead><tr><th>Work category</th><th>Visible task status</th></tr></thead><tbody>${rows}</tbody></table>` +
              `<p>${twin.actual_hours} recorded hours · ${twin.task_cost} ${escape(twin.currency)} task cost</p>` +
              `<p>Work needing attention: ${twin.readiness.overdue} overdue · ${twin.readiness.undated} undated · ${twin.readiness.unassigned} unassigned. Counts may overlap.</p>` +
              `<p>Business execution only. Railway release remains in OpenSourceRail.</p>` });
        },
      });
    }, __("OpenSourceRail"));
  },
});

frappe.ui.form.on('Project', {
  refresh(frm) {
    if (frm.is_new() || !frm.doc.custom_osr_city) return;
    frm.add_custom_button(__('Operating components'), async () => {
      const {message: catalogue} = await frappe.call({type: 'GET', method: 'osr_erpnext.components.catalogue', args: {project: frm.doc.name}});
      const chooser = new frappe.ui.Dialog({title: __('Choose operating component'), fields: [
        {fieldname: 'component', label: __('Component'), fieldtype: 'Select', reqd: 1,
          options: Object.entries(catalogue.components).map(([value, spec]) => ({value, label: spec.label}))},
      ], primary_action_label: __('Configure'), primary_action({component}) {
        chooser.hide(); configure(component, catalogue.components[component], catalogue.defaults[component] || {});
      }});
      chooser.show();
      function configure(component, spec, defaults) {
        const escape = frappe.utils.escape_html;
        const fields = JSON.parse(JSON.stringify(spec.fields));
        for (const field of fields) {
          if (Object.hasOwn(defaults, field.fieldname)) field.default = defaults[field.fieldname];
          if (field.fieldtype === 'Table') {field.cannot_add_rows = false; field.in_place_edit = true;}
          if (field.options === 'Warehouse') field.get_query = () => ({filters: {name: ['in', catalogue.warehouses]}});
        }
        if (component === 'quality') {
          const line = fields.find(f => f.fieldname === 'line');
          line.label = 'Receipt / invoice item'; line.fieldtype = 'Select'; line.options = [''];
          fields.find(f => f.fieldname === 'reference_type').onchange = () => {
            dialog.set_df_property('reference', 'options', dialog.get_value('reference_type'));
            dialog.set_value('reference', ''); dialog.set_value('line', '');
          };
          fields.find(f => f.fieldname === 'reference').onchange = async () => {
            const reference = dialog.get_value('reference');
            const reference_type = dialog.get_value('reference_type');
            dialog.set_value('line', '');
            if (!reference) return;
            const {message: rows} = await frappe.call({type: 'GET', method: 'osr_erpnext.components.inspection_lines',
              args: {project: frm.doc.name, reference_type, reference}});
            if (dialog.get_value('reference') === reference && dialog.get_value('reference_type') === reference_type)
              dialog.set_df_property('line', 'options', [{value: '', label: ''}, ...rows]);
          };
        }
        const pick = (schema, data) => Object.fromEntries(schema.filter(f => data[f.fieldname] !== undefined).map(f =>
          [f.fieldname, f.fieldtype === 'Table' ? (data[f.fieldname] || []).map(row => pick(f.fields, row)) : data[f.fieldname]]));
        const dialog = new frappe.ui.Dialog({title: spec.label, size: 'large', fields: [
          {fieldname: 'effect', fieldtype: 'HTML', options: `<p>${escape(spec.effect)}</p><p>${escape(catalogue.city)} · ${escape(catalogue.company)} · ${escape(catalogue.currency)}</p>`},
          {fieldname: 'instance_key', label: __('Instance key'), fieldtype: 'Data', reqd: 1,
            description: 'A stable name such as depot-spares. Reuse it to reopen the same record.'},
          ...fields,
        ], primary_action_label: __('Preview'), async primary_action(values) {
          const inputs = pick(spec.fields, values);
          const args = {project: frm.doc.name, component, key: values.instance_key, inputs};
          const {message: plan} = await frappe.call({method: 'osr_erpnext.components.preview', args, freeze: true});
          const rows = spec.fields.filter(f => inputs[f.fieldname] !== undefined).map(f => {
            const value = f.fieldtype === 'Table' ? inputs[f.fieldname].map(row => Object.values(row).join(' · ')).join('; ') : inputs[f.fieldname];
            return `<tr><th>${escape(f.label)}</th><td>${escape(String(value))}</td></tr>`;
          }).join('');
          const review = new frappe.ui.Dialog({title: __('Review component'), size: 'large', fields: [
            {fieldtype: 'HTML', options: `<p>${escape(plan.effect)}</p><p>Native record: ${escape(plan.document.doctype)}</p><table class="table">${rows}</table>`},
          ], primary_action_label: __('Apply component'), async primary_action() {
            const {message: result} = await frappe.call({method: 'osr_erpnext.components.apply', args: {...args, fingerprint: plan.fingerprint}, freeze: true});
            review.hide(); dialog.hide(); frappe.set_route('Form', result.doctype, result.name);
          }});
          review.show();
        }});
        dialog.show();
      }
    }, __('OpenSourceRail'));
  },
});
