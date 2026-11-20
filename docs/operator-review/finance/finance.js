const el = id => document.getElementById(id);
const money = value => '$' + value.toLocaleString('en-US', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + 'm';
const names = {budget_only:'Public budget', mixed_debt:'50% debt · 4% · 20 years', shorter_costlier_mixed_debt:'50% debt · 7% · 12 years', export_slice:'Export-credit illustration · 4% · 15 years'};
for (const [key, railway] of Object.entries(railwayFinance)) el('network').add(new Option(railway.label,key));
const query = new URLSearchParams(window.location.search);
const initialNetwork = query.get('network');
const mainlineKey = 'metropolitan-mainlines';
const initialOperation = query.get('operation') || 'full';
const matchesNetwork = initialOperation === 'full' || (initialOperation === mainlineKey && initialNetwork === 'metropolitan');
const amount = query.get('opex');
const scenarioBudget = amount?.trim() ? Number(amount) : NaN;
let appliedStaffBudget = matchesNetwork && Object.hasOwn(railwayFinance, initialNetwork) &&
    Number.isFinite(scenarioBudget) && scenarioBudget > 0 ? scenarioBudget : null;

function selectRailway() {
    const previous = el('terms').value;
    const {cases} = railwayFinance[el('network').value];
    el('terms').replaceChildren();
    for (const key of Object.keys(cases)) el('terms').add(new Option(names[key],key));
    el('terms').value = previous in cases ? previous : 'mixed_debt';
    draw();
}
function draw() {
    const core = el('network').value === 'core';
    const selected = railwayFinance[el('network').value].cases[el('terms').value];
    const citywide = el('network').value === 'metropolitan';
    el('operation-label').hidden = !citywide;
    const operation = citywide ? el('operation').value : 'full';
    const mainlines = operation === mainlineKey;
    const useStaffBudget = appliedStaffBudget !== null && el('network').value === initialNetwork && operation === initialOperation;
    const operatingAllowance = useStaffBudget ? appliedStaffBudget : mainlines
        ? workforceStudy.operating_options[mainlineKey].opex.baseline_usd_m_year : null;
    el('operating-basis').hidden = !mainlines;
    el('operating-basis').textContent = mainlines
        ? 'Fourteen main routes run with five access sections deferred. This comparison funds all citywide infrastructure, stations and the fleet. Train operations and electricity follow the diagrammed mileage.' : '';
    el('staffing-case').hidden = !useStaffBudget;
    const rows = selected.annual.map(row => {
        if (operatingAllowance === null || row.operations === 0) return row;
        return {...row, operations: operatingAllowance,
            buyer_cash: row.buyer_cash - row.operations + operatingAllowance};
    });
    const opening = rows.find(row => row.operations > 0);
    const total = key => rows.reduce((sum,row) => sum + row[key],0);
    const year = value => core ? 'Year ' + value : String(value);
    el('capital').textContent = money(total('capital'));
    el('borrow').textContent = money(total('borrowing'));
    el('service').textContent = money(selected.annual_debt_service);
    el('opex').textContent = money(opening.operations);
    el('opening').textContent = year(opening.year) + ' needs ' + money(opening.buyer_cash) + ' before receipts. During construction the largest annual buyer draw is ' +
        money(Math.max(...rows.filter(r => r.capital > 0).map(r => r.buyer_cash))) + '. Construction interest totals ' + money(selected.construction_interest) + '.';
    const inputs = [el('journeys'),el('fare')];
    const valid = inputs.every(input => input.value !== '' && input.validity.valid && Number.isFinite(input.valueAsNumber));
    const receipts = el('journeys').valueAsNumber * el('fare').valueAsNumber;
    const gap = opening.buyer_cash - receipts;
    el('support').textContent = valid && Number.isFinite(gap) ? 'Annual fare receipts of ' + money(receipts) + ' leave ' + money(Math.abs(gap)) +
        (gap >= 0 ? ' to fund from other sources.' : ' above this year’s gross requirement.') : 'Enter paid journeys and the net receipt per journey to test the opening-year public contribution.';
    const peak = Math.max(...rows.map(row => row.buyer_cash));
    el('bars').replaceChildren(); el('rows').replaceChildren();
    for (const r of rows) {
        const bar = document.createElement('span');
        bar.className = r.capital ? 'bar cap' : 'bar';
        bar.style.height = (100*r.buyer_cash/peak) + '%';
        bar.title = year(r.year) + ' · ' + money(r.buyer_cash);
        el('bars').append(bar);
        const line = el('rows').insertRow();
        line.insertCell().textContent = year(r.year);
        for (const key of ['capital','borrowing','interest','principal','operations','renewals','buyer_cash','closing_debt'])
            line.insertCell().textContent = r[key].toFixed(1);
    }
    el('start').textContent = year(rows[0].year);
    el('end').textContent = year(rows.at(-1).year);
    el('basis').textContent = core ? 'Core funding assumption: equal monthly capital draws across the 43-month construction plan. Costs of initial trials sit in capital. The first full service budget starts in Year 5. Rephase the intervening months and supplier milestones once opening dates are available.' :
        'Baghdad uses the published annual construction draws. The 2027 start and full opening years are planning assumptions. The earlier procurement did not secure a delivery contractor. Lenders and public funding have yet to commit.';
}
el('network').value = Object.hasOwn(railwayFinance, initialNetwork) ? initialNetwork : 'first';
el('operation').value = matchesNetwork ? initialOperation : 'full';
el('operation').addEventListener('change',draw);
el('restore-budget').addEventListener('click', () => {
    appliedStaffBudget = null;
    draw();
});
el('network').addEventListener('change',selectRailway);
for (const id of ['terms','journeys','fare']) el(id).addEventListener('input',draw);
selectRailway();
