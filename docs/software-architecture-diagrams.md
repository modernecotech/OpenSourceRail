# Software Architecture Diagrams

These diagrams expand the system map in
[`ARCHITECTURE.md`](ARCHITECTURE.md) and the crate allocations in
[`RFC 0005`](rfcs/0005-sbc-software-architecture.md). They are intended
as editable architecture drawings for implementers, operators, and
reviewers.

## 1. Deployment Context

```mermaid
flowchart LR
  subgraph BackOffice["OCC and Back Office"]
    OCC["osr-occ\noperations control"]
    OpsPortal["operations portal\nOps Core + SQLite"]
    Historian["osr-historian\ntelemetry archive"]
    Analytics["osr-analytics\nKPIs and reports"]
    CBM["osr-cbm-backend\ncondition maintenance"]
    AFCBack["osr-afc-backoffice\nfare settlement"]
  end

  subgraph Depot["Depot and Production Plant"]
    DepotSBC["S-SBC depot host"]
    Workshop["tooling, fixtures,\ncalibration records"]
    FleetMaint["fleet maintenance\nwork orders"]
    DepotEnergy["depot PV, BESS,\nslow charging"]
  end

  subgraph Stations["Stations"]
    StationSBC["S-SBC station host"]
    AFC["osr-afc / osr-tvm"]
    PIS["osr-pis-station"]
    PSD["osr-psd"]
    StationSCADA["osr-station-scada"]
    StationEnergy["chargers, PV,\nstation BESS"]
  end

  subgraph Wayside["Wayside and Waypoint Nodes"]
    WSBC["W-SBC"]
    Points["osr-wayside-points"]
    Balise["osr-balise / beacons"]
    Intrusion["osr-intrusion-detect"]
    Crossing["osr-level-crossing"]
    HABD["osr-hot-axle-wayside"]
  end

  subgraph Train["Trainset"]
    SafetyECU["T-ECU/S safety"]
    AppECU["T-ECU/A applications"]
    TOBS["T-OBS obstacle detection"]
    Trainbus["TCN-E TSN trainbus"]
  end

  Passenger["Passengers\nmobile money / QR / NFC"]
  Utility["Grid / PPA / export"]
  Regulator["Owner engineer / ISA /\nregulator evidence"]

  OCC <--> OpsPortal
  OCC <--> Historian
  Historian --> Analytics
  Historian --> CBM
  OpsPortal <--> FleetMaint
  OpsPortal --> Regulator
  AFCBack <--> AFC
  Passenger <--> AFC
  OCC <--> StationSBC
  OCC <--> WSBC
  OCC <--> SafetyECU
  StationEnergy <--> Utility
  DepotEnergy <--> Utility
  StationEnergy <--> Trainbus
  WSBC <--> SafetyECU
  Trainbus <--> SafetyECU
  Trainbus <--> AppECU
  Trainbus <--> TOBS
  DepotSBC <--> AppECU
  DepotSBC <--> Workshop
```

## 2. Backend / OCC Services

```mermaid
flowchart TB
  subgraph Ingest["Ingest"]
    TrainReports["train reports\nposition, SoC, faults"]
    WaysideReports["wayside reports\nswitch, intrusion, HABD"]
    StationReports["station reports\nAFC, PSD, SCADA"]
    EnergyReports["energy reports\nPV, BESS, chargers"]
  end

  subgraph EventCore["Event Core"]
    OpsLog["authoritative ops log\nNATS JetStream / append-only"]
    ReadModels["read models\ncurrent network state"]
    Audit["audit stream\nsafety and operations events"]
  end

  subgraph Services["Backend Services"]
    OccSvc["osr-occ\nATS, incidents, dispatch"]
    Routing["osr-routing\nroute proposals"]
    Historian["osr-historian\ntime-series retention"]
    CbmBackend["osr-cbm-backend\nmaintenance triggers"]
    Analytics["osr-analytics\navailability, kWh/km, MDBF"]
    AfcBack["osr-afc-backoffice\nsettlement and fraud checks"]
    OpsCore["Ops Core API\nSQLite work orders"]
  end

  subgraph Interfaces["User Interfaces"]
    Dispatcher["dispatcher console"]
    Portal["operations portal"]
    Reports["monthly reports"]
    Maintainer["maintenance view"]
  end

  TrainReports --> OpsLog
  WaysideReports --> OpsLog
  StationReports --> OpsLog
  EnergyReports --> OpsLog
  OpsLog --> ReadModels
  OpsLog --> Audit
  ReadModels --> OccSvc
  ReadModels --> Routing
  OpsLog --> Historian
  Historian --> CbmBackend
  Historian --> Analytics
  StationReports --> AfcBack
  CbmBackend --> OpsCore
  OccSvc --> Dispatcher
  OpsCore --> Portal
  OpsCore --> Maintainer
  Analytics --> Reports
  Audit --> Portal
```

## 3. Onboard Train Software

```mermaid
flowchart TB
  subgraph TECUS["T-ECU/S Safety Kernel"]
    ATP["osr-atp\nmovement authority envelope"]
    Odo["osr-odometry\nposition fusion"]
    Brake["osr-brake\nEP brake + WSP"]
    Traction["osr-traction\ninverter control"]
    BMS["osr-bms\nbattery safety"]
    Door["osr-door-control\nclosing interlock"]
    Fire["osr-fire-safety"]
    Derail["osr-derailment"]
  end

  subgraph TECUA["T-ECU/A Applications"]
    ATO["osr-ato\ndrive target inside ATP envelope"]
    TCMS["osr-tcms\ntrain management"]
    T2G["osr-t2g\n5G + LoRa train-ground"]
    EventRec["osr-event-recorder"]
    Regen["osr-regen"]
    Aux["osr-aux-power"]
    HVAC["osr-hvac"]
    Lighting["osr-lighting"]
    PIS["osr-pis-onboard"]
    CBMOn["osr-cbm-onboard"]
  end

  subgraph TOBS["T-OBS"]
    Obstacle["osr-obstacle-detect\nClear / Crawl / EB"]
  end

  subgraph Bus["On-Train Networks"]
    TCNE["TCN-E TSN Ethernet"]
    CAN["CAN-FD segments"]
    PTP["osr-ptp time sync"]
  end

  subgraph Hardware["Actuators and Sensors"]
    Motors["traction motors"]
    Brakes["brake actuators"]
    Doors["door drives and locks"]
    Battery["battery strings"]
    Sensors["tachos, IMU, GNSS,\nbeacons, cameras, radar"]
  end

  T2G --> ATP
  T2G --> Odo
  Odo --> ATP
  ATP --> Brake
  ATP --> ATO
  ATO --> Traction
  Traction --> Motors
  Brake --> Brakes
  BMS --> Battery
  Door --> Doors
  Obstacle --> ATP
  Fire --> ATP
  Derail --> ATP
  Sensors --> Odo
  Sensors --> Obstacle
  TCMS <--> TCNE
  ATP <--> TCNE
  Brake <--> CAN
  Door <--> CAN
  TCNE <--> PTP
  TCMS --> EventRec
  TCMS --> CBMOn
  CBMOn --> T2G
  PIS --> TCMS
  HVAC --> TCMS
  Lighting --> TCMS
```

## 4. Station and Depot Software

```mermaid
flowchart TB
  subgraph SSBC["S-SBC Station / Depot Host"]
    StationAgent["station agent\nhealth and config"]
    PISStation["osr-pis-station\nPIS and PA"]
    AFC["osr-afc\nfare gates"]
    TVM["osr-tvm\nticket vending"]
    PSD["osr-psd\nplatform doors"]
    Scada["osr-station-scada\nlifts, HVAC, CCTV"]
    EnergySite["osr-energy-site\nPV, BESS, chargers"]
    SelfTest["osr-selftest\nrole checks"]
  end

  subgraph LocalDevices["Local Devices"]
    Displays["platform displays"]
    Speakers["PA speakers"]
    Gates["fare gates"]
    Chargers["station chargers"]
    BESS["station battery"]
    Lifts["lifts and escalators"]
    CCTV["CCTV / NVR"]
    FirePanel["fire panel"]
    DepotTools["depot tools and fixtures"]
  end

  subgraph Backhaul["Backhaul"]
    OCC["OCC event stream"]
    OpsCore["Ops Core SQLite API"]
    AFCBack["AFC back office"]
    Historian["historian"]
  end

  PISStation --> Displays
  PISStation --> Speakers
  AFC --> Gates
  TVM --> Gates
  PSD --> Displays
  Scada --> Lifts
  Scada --> CCTV
  Scada --> FirePanel
  EnergySite --> Chargers
  EnergySite --> BESS
  StationAgent --> SelfTest
  StationAgent --> OCC
  EnergySite --> Historian
  Scada --> Historian
  AFC --> AFCBack
  SelfTest --> OpsCore
  DepotTools --> OpsCore
```

## 5. Wayside / Waypoint Node Software

In OSR language, a "waypoint" is any fixed railway location that helps
localize, command, observe, or protect the railway: balise/beacon,
switch, crossing, platform edge, intrusion sensor, hot-axle detector, or
energy/charger site.

```mermaid
flowchart TB
  subgraph WSBC["W-SBC Cabinet"]
    Consensus["osr-consensus\ntrack-state replica"]
    Interlocking["osr-interlocking\nMA and route safety"]
    Points["osr-wayside-points\npoint command and detection"]
    Balise["osr-balise\nfixed position reference"]
    Crossing["osr-level-crossing"]
    HABD["osr-hot-axle-wayside"]
    Intrusion["osr-intrusion-detect"]
    PTP["osr-ptp"]
    Crypto["osr-crypto\nmTLS and signed firmware"]
    SelfTest["osr-selftest"]
  end

  subgraph FieldIO["Field I/O"]
    PointMotor["BLDC point motor"]
    PointSensors["dual point sensors"]
    Beacon["balise / UWB beacon"]
    Barrier["crossing barriers"]
    Thermal["hot axle IR array"]
    Fence["intrusion sensors"]
    UPS["cabinet PSU / UPS"]
  end

  subgraph Network["Networks"]
    WayE["WAY-E TSN Ethernet"]
    TrainRadio["train-ground radio\n5G / LoRa"]
    OCC["OCC / ops event stream"]
  end

  WayE <--> Consensus
  Consensus <--> Interlocking
  Interlocking --> Points
  Points --> PointMotor
  PointSensors --> Points
  Balise --> Beacon
  Crossing --> Barrier
  Thermal --> HABD
  Fence --> Intrusion
  PTP --> WayE
  Crypto --> WayE
  SelfTest --> OCC
  Interlocking <--> TrainRadio
  HABD --> Consensus
  Intrusion --> Consensus
  Crossing --> Consensus
  UPS --> SelfTest
```

## 6. Control and Data Flow

```mermaid
sequenceDiagram
  participant Dispatcher as Dispatcher Console
  participant OCC as osr-occ
  participant Log as Ops Event Log
  participant W as W-SBC Consensus + Interlocking
  participant Train as Train T-ECU/S + T-ECU/A
  participant Hist as Historian / CBM
  participant Core as Ops Core

  Dispatcher->>OCC: request route / timetable action
  OCC->>Log: append dispatch intent
  Log->>W: route proposal
  W->>W: verify track state and point locks
  W->>Train: movement authority
  Train->>Train: ATP computes permitted envelope
  Train->>Train: ATO commands traction/brake within envelope
  Train->>W: position report and health heartbeat
  Train->>Log: telemetry and service events
  W->>Log: switch state, intrusion, HABD, route state
  Log->>Hist: telemetry archive
  Hist->>Core: condition trigger / work-order suggestion
  Core->>Dispatcher: open work, holds, defects, evidence state
```

## 7. Energy and Charging Software

```mermaid
flowchart LR
  subgraph Planning["Planning and Supervision"]
    OCC["osr-occ\ntimetable and train location"]
    EnergyPlanner["charging dispatch\nI9"]
    Historian["historian\nenergy telemetry I10"]
  end

  subgraph TrainEnergy["Train"]
    BMS["osr-bms\nSoC, SoH, thermal limits"]
    ATO["osr-ato\nenergy-aware driving"]
    Regen["osr-regen\nregen routing"]
    ChargerIF["charge interface"]
  end

  subgraph Site["Station / Depot Energy Site"]
    EnergySite["osr-energy-site\nsite controller"]
    PV["PV inverter"]
    BESS["station BESS"]
    Charger["platform / depot charger"]
    Grid["grid tie\nIEEE 2030.5 / SunSpec"]
  end

  OCC --> EnergyPlanner
  BMS --> Historian
  EnergySite --> Historian
  Historian --> EnergyPlanner
  EnergyPlanner --> EnergySite
  EnergyPlanner --> ATO
  ATO --> BMS
  BMS --> ChargerIF
  Regen --> ChargerIF
  PV --> EnergySite
  BESS --> EnergySite
  EnergySite --> Charger
  Charger --> ChargerIF
  EnergySite <--> Grid
```

## 8. QA, Maintenance, and Evidence Flow

```mermaid
flowchart TB
  subgraph Generated["Generated Design Data"]
    DesignToml["city design.toml"]
    ScenarioToml["scenario toml"]
    QATemplate["construction-qa.toml"]
    MaintTemplate["maintenance-schedule.toml"]
  end

  subgraph PortalData["Portal Data Generator"]
    Generator["generate-qa-maintenance-data.py"]
    AssetCSV["asset register CSV"]
    QACSV["QA action CSV"]
    MaintCSV["maintenance schedule CSV"]
    Bundle["operations JSON bundle"]
  end

  subgraph OpsCore["Ops Core Runtime"]
    Portal["browser portal"]
    SQLite["ops-core.sqlite3"]
    Reconcile["storage reconciliation\nlocal fallback to SQLite"]
    WorkOrders["work orders"]
    Inspections["inspection evidence"]
    Defects["defects / NCR"]
    Audit["audit trail"]
  end

  subgraph Evidence["Evidence Consumers"]
    Maintainer["maintainers"]
    OwnerEngineer["owner engineer"]
    Regulator["regulator / ISA"]
    Reports["CSV exports and reports"]
  end

  DesignToml --> Generator
  ScenarioToml --> Generator
  QATemplate --> Generator
  MaintTemplate --> Generator
  Generator --> AssetCSV
  Generator --> QACSV
  Generator --> MaintCSV
  Generator --> Bundle
  Bundle --> Portal
  Portal <--> SQLite
  Portal <--> Reconcile
  Reconcile --> SQLite
  Portal --> WorkOrders
  WorkOrders --> Inspections
  Inspections --> Defects
  WorkOrders --> Audit
  Defects --> Audit
  Audit --> Reports
  Maintainer --> Portal
  OwnerEngineer --> Portal
  Regulator --> Reports
```

## 9. Safety and Security Boundaries

```mermaid
flowchart TB
  subgraph SIL4["SIL-4 Safety Kernel"]
    Interlocking["osr-interlocking"]
    Consensus["osr-consensus"]
    ATP["osr-atp"]
    Odo["osr-odometry"]
    Brake["osr-brake"]
    DoorClose["door closing interlock"]
    Obstacle["osr-obstacle-detect"]
    Points["osr-wayside-points"]
  end

  subgraph SIL2["SIL-2 Safety Adjacent"]
    ATO["osr-ato"]
    TCMS["osr-tcms"]
    TCN["osr-tcn"]
    T2G["osr-t2g"]
    PSD["osr-psd"]
    Energy["osr-energy-site"]
    StationSCADA["osr-station-scada"]
  end

  subgraph SIL0["SIL-0 Supervisory and UX"]
    OCC["osr-occ UI"]
    Portal["operations portal"]
    Historian["osr-historian"]
    Analytics["osr-analytics"]
    PIS["passenger information"]
    AFC["fare collection"]
  end

  subgraph Security["Security Controls"]
    Crypto["osr-crypto"]
    PTP["osr-ptp"]
    SelfTest["osr-selftest"]
    Firmware["signed firmware /\nmeasured boot"]
  end

  OCC -->|requests only| ATO
  Portal -->|work orders only| StationSCADA
  ATO -->|bounded commands| ATP
  TCMS -->|bounded train commands| Brake
  Energy -->|charging limits| BMS
  Interlocking -->|movement authority| ATP
  ATP -->|safe state| TCMS
  TCMS -->|events| OCC
  StationSCADA -->|events| Portal
  Crypto --> SIL4
  Crypto --> SIL2
  PTP --> SIL4
  SelfTest --> SIL2
  Firmware --> SIL4
  Firmware --> SIL2
```
