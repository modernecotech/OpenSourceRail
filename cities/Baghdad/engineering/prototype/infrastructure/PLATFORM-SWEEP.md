# Airport platform edge and doorway curve screen

A straight 75 mm platform offset carried around a curve can intersect the nominal car. The table gives the minimum inside-curve and outside-curve body separation over the whole car and the minimum and maximum at each doorway. Negative values indicate geometric overlap. All gaps are radial millimetres, rounded to the nearest millimetre. Symmetric door positions share a row.

| Illustrative radius, m | Body or door centre from car midpoint | Inside platform gap, mm | Outside platform gap, mm |
|---:|---|---:|---:|
| 150 | Whole body minimum | -62 | -27 |
| 150 | ±2.1 m door | -55 to -36 | 186 to 205 |
| 150 | ±6.3 m door | 45 to 102 | 51 to 107 |
| 250 | Whole body minimum | -7 | 13 |
| 250 | ±2.1 m door | -3 to 9 | 142 to 153 |
| 250 | ±6.3 m door | 57 to 91 | 60 to 94 |
| 500 | Whole body minimum | 34 | 44 |
| 500 | ±2.1 m door | 36 to 42 | 108 to 114 |
| 500 | ±6.3 m door | 66 to 83 | 67 to 84 |

The car is a rigid 17 m rectangle on two pivots 12.8 m apart. The example uses concentric track and platform arcs, a 2.70 m wide body and a 1.36 m rough opening at each door. Each side of the rectangle follows the chord between the pivots. Its radial distance increases from the car midpoint towards the ends. The straight case gives 75 mm at every point. The three radii reproduce the existing mechanical screen and have no surveyed station assignment.

Use the whole-body minimum to identify interference even when door gaps appear clear. Moving an edge away from the train increases both the minimum clearance and the largest boarding gap on that side. Before locating an edge, survey track curvature, transitions, cant and stopping range over the platform. Add wheel and track wear, lateral and vertical suspension travel, installed threshold projection, body deflection, construction tolerance and permitted gap and step limits. Survey all 24 boarding zones and retain accessible boarding and clearance results separately.

Airport physical candidate `b38d4bd348cc57d8f3fab9696df06e5b35ba51380670aa8e566b7f89d9c5da01`. Vehicle arrangement evaluation `b866da14b4d3c78cd90598d1a7cfc12548fd548f8cf1c7651e725a45568a3c89`. Civil evaluation `9920c8a2cb8c7e1c4a8415c5272349124f09a92e5003c75bd20d7fea69fecbc8`.

[Vehicle arrangement](../vehicle-factory/INSTALLED-GA.md) · [Station enquiry](STATION.md) · [Calculation](platform_sweep.py)
