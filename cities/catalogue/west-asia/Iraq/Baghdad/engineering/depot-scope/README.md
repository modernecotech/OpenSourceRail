# baghdad depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-2-0595-0296-s052851 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-2500-0775-s000000 | line-1 | 63 | 6,993.0 | 7,623.0 | unverified |
| line-1-0166-0866-s049067 | line-1 | 63 | 6,993.0 | 7,623.0 | unverified |
| line-2-1987-2192-s000000 | line-2 | 62 | 6,882.0 | 7,502.0 | unverified |
| line-2-0595-0296-s052851 | line-2 | 61 | 6,771.0 | 7,381.0 | unverified |
| line-3-2271-1120-s000000 | line-3 | 57 | 6,327.0 | 6,897.0 | unverified |
| line-3-0151-1637-s049496 | line-3 | 56 | 6,216.0 | 6,776.0 | unverified |
| line-4-0146-0199-s000000 | line-4 | 49 | 5,439.0 | 5,929.0 | unverified |
| line-4-1230-1627-s041932 | line-4 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-5-1199-0260-s000000 | line-5 | 58 | 6,438.0 | 7,018.0 | unverified |
| line-5-0677-2304-s047345 | line-5 | 58 | 6,438.0 | 7,018.0 | unverified |
| line-6-2322-0251-s000000 | line-6 | 60 | 6,660.0 | 7,260.0 | unverified |
| line-6-0495-1669-s052503 | line-6 | 59 | 6,549.0 | 7,139.0 | unverified |
| line-7-1069-2206-s000000 | line-7 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-7-1531-0418-s039957 | line-7 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-8-2231-1783-s000000 | line-8 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-8-0785-0290-s048137 | line-8 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-9-0645-0595-s000803 | line-9 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-9-0750-0579-s095874 | line-9 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-10-0463-0842-s000000 | line-10 | 9 | 999.0 | 1,089.0 | unverified |
| line-10-0529-1057-s006497 | line-10 | 8 | 888.0 | 968.0 | unverified |
| line-11-0789-1053-s000000 | line-11 | 13 | 1,443.0 | 1,573.0 | unverified |
| line-11-0787-0835-s006598 | line-11 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-12-0910-1275-s000000 | line-12 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-12-0634-1426-s007727 | line-12 | 11 | 1,221.0 | 1,331.0 | unverified |
| line-13-0948-1130-s000000 | line-13 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-13-1187-0913-s007284 | line-13 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-14-1241-0448-s000000 | line-14 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-14-1491-0559-s006809 | line-14 | 9 | 999.0 | 1,089.0 | unverified |
| line-15-0891-0409-s000000 | line-15 | 15 | 1,665.0 | 1,815.0 | unverified |
| line-15-1354-0099-s012109 | line-15 | 15 | 1,665.0 | 1,815.0 | unverified |
| line-16-1114-1355-s000000 | line-16 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-16-0963-1569-s006581 | line-16 | 11 | 1,221.0 | 1,331.0 | unverified |
| line-17-1295-0780-s000000 | line-17 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-17-1265-0501-s007000 | line-17 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-18-0316-0338-s000000 | line-18 | 11 | 1,221.0 | 1,331.0 | unverified |
| line-18-0062-0637-s008849 | line-18 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-19-0278-1605-s000000 | line-19 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-19-0062-1487-s006741 | line-19 | 9 | 999.0 | 1,089.0 | unverified |
| line-20-0738-0836-s000000 | line-20 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-20-0937-0562-s007187 | line-20 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-21-1210-0385-s000000 | line-21 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-21-1286-0064-s007539 | line-21 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-22-0847-0481-s000000 | line-22 | 9 | 999.0 | 1,089.0 | unverified |
| line-22-0676-0325-s006216 | line-22 | 8 | 888.0 | 968.0 | unverified |
| line-23-0547-1101-s000000 | line-23 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-23-0307-0836-s010462 | line-23 | 13 | 1,443.0 | 1,573.0 | unverified |
| line-24-1354-0628-s000000 | line-24 | 16 | 1,776.0 | 1,936.0 | unverified |
| line-24-1517-0884-s010989 | line-24 | 15 | 1,665.0 | 1,815.0 | unverified |
| line-25-1267-1362-s000000 | line-25 | 11 | 1,221.0 | 1,331.0 | unverified |
| line-25-1421-1273-s006023 | line-25 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-26-0220-0251-s000000 | line-26 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-26-0060-0163-s006894 | line-26 | 9 | 999.0 | 1,089.0 | unverified |
| line-27-0982-0998-s000000 | line-27 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-27-1173-0669-s011748 | line-27 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-28-0617-1563-s000000 | line-28 | 13 | 1,443.0 | 1,573.0 | unverified |
| line-28-0138-1512-s010069 | line-28 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-29-1199-0261-s000000 | line-29 | 15 | 1,665.0 | 1,815.0 | unverified |
| line-29-1079-0406-s006094 | line-29 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-30-1340-1101-s000000 | line-30 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-30-1687-1287-s008895 | line-30 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-31-0337-0356-s000000 | line-31 | 16 | 1,776.0 | 1,936.0 | unverified |
| line-31-0762-0583-s014119 | line-31 | 16 | 1,776.0 | 1,936.0 | unverified |
| line-32-0885-1166-s000000 | line-32 | 13 | 1,443.0 | 1,573.0 | unverified |
| line-32-1062-1537-s009251 | line-32 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-33-1199-0260-s000000 | line-33 | 13 | 1,443.0 | 1,573.0 | unverified |
| line-33-1039-0043-s006507 | line-33 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-34-0710-0428-s000000 | line-34 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-34-0812-0713-s007493 | line-34 | 11 | 1,221.0 | 1,331.0 | unverified |
| line-35-0224-0830-s000000 | line-35 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-35-0587-0714-s010168 | line-35 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-36-0462-0842-s000000 | line-36 | 13 | 1,443.0 | 1,573.0 | unverified |
| line-36-0636-0641-s009660 | line-36 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-37-1093-1200-s000000 | line-37 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-37-1176-0827-s009972 | line-37 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-38-1296-1255-s000000 | line-38 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-38-1274-1173-s006028 | line-38 | 9 | 999.0 | 1,089.0 | unverified |
| line-39-0936-0727-s000000 | line-39 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-39-0863-0988-s006036 | line-39 | 9 | 999.0 | 1,089.0 | unverified |
| line-40-0368-1585-s000000 | line-40 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-40-0620-1397-s007371 | line-40 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-41-0566-0988-s000000 | line-41 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-41-0838-1262-s008284 | line-41 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-42-0171-0837-s000000 | line-42 | 8 | 888.0 | 968.0 | unverified |
| line-42-0037-0562-s006756 | line-42 | 8 | 888.0 | 968.0 | unverified |
| line-43-1199-0260-s000000 | line-43 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-43-0963-0288-s006892 | line-43 | 17 | 1,887.0 | 2,057.0 | unverified |
| line-44-1415-1534-s000000 | line-44 | 16 | 1,776.0 | 1,936.0 | unverified |
| line-44-1112-1286-s012476 | line-44 | 16 | 1,776.0 | 1,936.0 | unverified |
| line-45-1067-0663-s000000 | line-45 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-45-0937-0362-s007718 | line-45 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-46-1338-0614-s000000 | line-46 | 13 | 1,443.0 | 1,573.0 | unverified |
| line-46-1187-0913-s007287 | line-46 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-47-1199-0260-s000000 | line-47 | 17 | 1,887.0 | 2,057.0 | unverified |
| line-47-1411-0050-s012244 | line-47 | 17 | 1,887.0 | 2,057.0 | unverified |
| line-48-0698-0947-s000000 | line-48 | 9 | 999.0 | 1,089.0 | unverified |
| line-48-0976-1018-s006380 | line-48 | 8 | 888.0 | 968.0 | unverified |
| line-49-1186-1057-s000000 | line-49 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-49-0966-1061-s007638 | line-49 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-50-1241-0448-s000000 | line-50 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-50-1138-0039-s013203 | line-50 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-51-0543-0944-s000000 | line-51 | 11 | 1,221.0 | 1,331.0 | unverified |
| line-51-0412-1213-s008699 | line-51 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-52-0442-0485-s000000 | line-52 | 15 | 1,665.0 | 1,815.0 | unverified |
| line-52-0887-0297-s011301 | line-52 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-53-0846-1385-s000000 | line-53 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-53-0855-0834-s011884 | line-53 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-54-0764-1598-s000000 | line-54 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-54-1095-1411-s009273 | line-54 | 13 | 1,443.0 | 1,573.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
