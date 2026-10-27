# v0.6 README illustration brief

These images present the v0.6 research configuration at repository revision
`b77f410f9fadfd0a8cce5404a2f98e0d3e808c9c`. They are concept artwork, not
supplier drawings, site layouts, numerical evidence or accepted safety designs.
The five WebP files are compressed display copies of the supplied PNGs, retained
under [docs/assets/v0.6](../../assets/v0.6/). Their
[catalogue](../../assets/v0.6/illustrations.json) maps original upload names,
source PNGs and display files. The prompts below record the supplied illustration
brief; they do not certify every detail visible in the images.

`v06-launch-to-arrival.svg` is an editable, deterministic explanatory drawing.
Its quantities follow the [current reference](../../design-engine/current/README.md)
and `station_zone()` in [operations.py](../../../engineering/station_rail/operations.py).
It does not plot a simulated or measured trajectory.

## Regeneration prompts and invariants

1. **`v06-hero-elevated-station.webp` - architectural hero.** Photorealistic wide 16:9 Baghdad-like elevated station scene showing a six-car, 17 m/car, driverless lightweight off-white GFRP/aluminium train; broad cabless end glazing, flush rooftop solar, two central side doors/car, all bogies supported on two steel running rails per direction, two repeatable precast guideways, slim pier structure, central platform and accessible flush lift. No catenary, maglev, major deck or fantasy infrastructure.
2. **`v06-cabin.webp` - passenger interior.** Photorealistic wide 16:9 passenger cabin, four-abreast fixed seating in seating zones, wall benches adjacent to accessible central passenger doors, wheelchair spaces, generous aisle, composite window recesses, integrated HVAC and lighting, broad glazed end, restrained colours. No large central standing saloon or driver cab. The precise 44-seat distribution is not certified by the illustration.
3. **`v06-assembly.webp` - offsite workshop assembly.** Photorealistic 16:9 raised three-quarter exploded workshop view of one 17 m composite/aluminium car, framed shells, roof solar, HVAC/ducting, window and door modules, benches, wiring, lightweight two-axle **passive** bogies, brake discs and passive aluminium LIM fin as separate modules installed on repeatable assembly jigs. Exclude traction motors, gearboxes and high-voltage drive cabling on the bogies; attachment method remains conceptual.
4. **`v06-viaduct-construction.webp` - civil prefabrication.** Photorealistic wide 16:9 repeated slender precast concrete rail girders, conventional running rails, columns and pier heads, mobile crane carefully lifting one prefabricated span from a trailer with temporary works and safely separated crew. Baghdad-like urban setting and small station beyond. No motorway deck, monorail, catenary or levitation.
5. **`v06-wayside-lim-cutaway.webp` - motor interface.** Photorealistic wide 16:9 close engineering cutaway of a steel-wheel passenger car on two steel rails over a precast guideway. A smooth **passive vertical aluminium secondary** hangs below the body between **two stationary wayside LIM primary coil faces** at a powered station approach; independent disc brakes on unpowered bogies. No onboard primary coils or traction motor, no magnet levitation or overhead electrification. The field and force are unverified.
6. **`v06-launch-to-arrival.svg` - explanatory system schematic.** A 2 km not-to-scale journey illustration with proposed powered launch, unpowered rolling, wayside receiving and independent friction-brake/ATP stopping. The current selected reference allocates **900 m of shared station winding per direction**, covering a calculated 496 m launch zone and 329 m receiving zone together; these are full-train engagement envelopes. The library allowance is not a 900 m motor in each approach and does not imply a 200 m coasting interval. Cross-section distinguishes supported wheel contact, wayside twin primaries and passive aluminium secondary. Available thrust remains open.

The renderings carry no quantitative labels; the SVG adds explicit schematic
quantities and limitations. Never use these assets as measured proof of safety,
minimum mass, clearance, accessibility, or physical performance.

## Reproduce the display copies

Keep the original PNGs. From the repository root, using the project's pinned
Pillow dependency, run:

```python
import json
from pathlib import Path
from PIL import Image

catalogue = json.loads(Path("docs/assets/v0.6/illustrations.json").read_text())
for item in catalogue["illustrations"]:
    with Image.open(item["file"]) as image:
        image.save(item["display_file"], format="WEBP", quality=88, method=6)
```

Dimensions remain 1672 by 941 pixels. The catalogue records the encoding-library
versions used for the checked-in copies. Original PNGs continue to supply the
illustrated PDF reader. Edit the SVG directly and recheck its numbers against
the current station model when the selected reference changes.
