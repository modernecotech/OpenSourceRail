# Software Architecture Diagrams

> **Operating architecture update:** [ERPNext + Frappe HR](operating/README.md) replace custom business administration. The diagrams below describe railway and existing assurance components; ERP cannot issue railway release authority.

These diagrams expand the system map in
[`ARCHITECTURE.md`](ARCHITECTURE.md) and the crate allocations in
[`RFC 0005`](rfcs/0005-sbc-software-architecture.md). They are intended
as editable architecture drawings for implementers, operators, and
reviewers.

## 1. Deployed Demonstration Platform

Solid arrows below describe the localhost demonstration. The Rust evaluators
run against simulation fixtures; this is not a commissioned railway deployment.
Native ERPNext and FUXA accounts retain their own permissions inside Workbench.

```mermaid
flowchart LR
  UI["Workbench: city and asset context"]
  Design["City Studio / FreeCAD / Bonsai IFC / QGIS"]
  Twin["Versioned engineering and city packages"]
  ERP["ERPNext + Frappe HR: native business transactions"]
  Gateway["OSR integration gateway: scoped API, SQLite history and durable outbox"]
  FUXA["FUXA: generated supervision views"]
  Native["Rust station / vehicle / wayside evaluators"]
  Fixture["Explicit simulation fixtures; factory-method rehearsal"]
  Railway["OSR simulation / OCC / railway works and handback"]
  Legacy["Historic Ops Core business records: read-only"]
  UI --> Design
  Design --> Twin
  Twin --> Gateway
  UI --> ERP
  UI --> FUXA
  UI --> Railway
  UI --> Gateway
  Fixture --> Native
  Native --> Gateway
  Fixture --> Gateway
  Gateway -->|deduplicated Issue / reviewed Asset Repair| ERP
  ERP -->|permission-filtered execution feedback| UI
  Gateway -->|REST tags / source quality| FUXA
  Legacy --> UI
```

ERP completion and alarm clearance cannot grant railway release or movement
authority. LM3 factory views apply only to the matching city family; cross-family
module reuse needs a separate reviewed mapping before it can be represented.

## 2. Integration Boundaries And Future Interfaces

```mermaid
flowchart TB
  Controllers["Native simulation controllers"]
  API["Implemented scoped HTTP integration API"]
  History["Gateway-owned SQLite historian and alarm/command audit"]
  Queue["Durable maintenance outbox"]
  ERP["ERPNext Issue / Asset Repair / stock / assignment"]
  FUXA["FUXA REST polling; DAQ disabled"]
  Hardware["Future commissioned supplier sensors and machines"]
  Transport["Future reviewed MQTT / OPC UA / Modbus adapters"]
  Bus["Future production event transport, e.g. NATS"]
  Assurance["Independent railway inspection and handback"]
  Controllers --> API
  API --> History
  History --> FUXA
  API --> Queue
  Queue --> ERP
  Hardware -.-> Transport
  Transport -.-> API
  API -.-> Bus
  ERP -.->|records for review; no release authority| Assurance
```

Dashed interfaces are proposed or require physical commissioning. NATS is not
the transport of the deployed ERPNext/FUXA demonstration. Shared identity, TLS,
backup operations, supplier bindings and HIL evidence remain deployment work.
The remaining diagrams describe intended railway allocations and interfaces;
they are not evidence that the depicted hardware paths have been commissioned.

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
    Gateway["OSR integration gateway"]
    ERP["ERPNext maintenance / tooling records"]
    Railway["OSR inspection and handback"]
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
  SelfTest -.-> Gateway
  DepotTools -.-> Gateway
  Gateway --> ERP
  Gateway --> Railway
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
  participant W as OSR shadow/supervised train-control candidate
  participant Train as Train T-ECU/S + T-ECU/A
  participant Hist as OSR historian / condition gateway
  participant Core as ERPNext maintenance
  participant Assurance as OSR independent handback

  Dispatcher->>OCC: request route / timetable action
  OCC->>Log: append dispatch intent
  Log->>W: route proposal
  W->>W: verify track state and point locks
  W-->>Train: candidate authority (shadow) / supervised request
  Train->>Train: ATP computes permitted envelope
  Train->>Train: ATO commands traction/brake within envelope
  Train->>W: position report and health heartbeat
  Train->>Log: telemetry and service events
  W->>Log: switch state, intrusion, HABD, route state
  Log->>Hist: telemetry archive
  Hist->>Core: condition trigger / work-order suggestion
  Core->>Dispatcher: maintenance case and repair status
  Core-->>Assurance: reviewed repair evidence for inspection
  Note over Core,Assurance: ERP completion grants no railway release
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

## 8. Manufacturing, QA, Maintenance, and Evidence Flow

```mermaid
flowchart TB
  Design["Versioned city design, assets and project twin"]
  Methods["LM3 methods, products, tooling and hold points"]
  Family["Selected city family applicability gate"]
  Mapping["Reviewed engineering revision + exact Item/BOM pair"]
  ERP["ERPNext: projects, procurement, production, stock, quality and repairs"]
  Workbench["Workbench: execution feedback and equipment context"]
  Gateway["OSR gateway: history, alarm queue and lifecycle evidence"]
  FUXA["FUXA: simulation method and equipment supervision"]
  Railway["OSR railway works, inspection and independent handback"]
  Legacy["Historic business records in Ops Core: read-only"]
  Physical["Open: performed travelers, machine adapters, physical measurements and rework disposition"]
  Design --> Mapping
  Mapping --> ERP
  Design --> Family
  Methods --> Family
  Family --> Gateway
  Gateway --> FUXA
  Gateway -->|condition-driven Issue| ERP
  ERP -->|permission-filtered actuals| Workbench
  Gateway --> Workbench
  Railway --> Workbench
  Legacy --> Workbench
  Physical -.-> ERP
  Physical -.-> Railway
```

Work Order correlation requires the Item and exact BOM from a single reviewed
mapping at the selected engineering revision. Factory views show method context
and simulation fixtures; they do not perform inspection, disposition or release.

## 9. Safety and Security Boundaries

```mermaid
flowchart TB
  subgraph SIL4["T1 / SIL-4 Target Safety Kernel"]
    Interlocking["osr-interlocking"]
    Consensus["osr-consensus"]
    ATP["osr-atp"]
    Odo["osr-odometry"]
    Brake["osr-brake"]
    DoorClose["door closing interlock"]
    Obstacle["osr-obstacle-detect"]
    Points["osr-wayside-points"]
  end

  subgraph SIL2["T2 / SIL-2 Target Safety Adjacent"]
    ATO["osr-ato"]
    TCMS["osr-tcms"]
    TCN["osr-tcn"]
    T2G["osr-t2g"]
    PSD["osr-psd"]
    Energy["osr-energy-site"]
    StationSCADA["osr-station-scada"]
  end

  subgraph SIL0["T3/T4 Supervisory and UX"]
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
