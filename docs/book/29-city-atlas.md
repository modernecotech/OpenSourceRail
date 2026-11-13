# Exploring the city atlas

The city atlas is an invitation to ask better questions about a place. It
joins a map to route proposals, station markers, service assumptions, energy,
fleet, civil quantities and costs. It also carries the source and uncertainty
behind those views. This is more informative than either a line drawn on a
street map or a single headline estimate, because the reader can examine
what the line is meant to do.

## Begin with the route and its neighbourhood

Choose a city, then follow one proposed line from end to end. Look for the
origins and destinations it connects, interchange opportunities and places
where the route crosses water, major roads or dense urban fabric. An
elevated guideway may reduce occupation at street level, but it needs
foundations, stations, access and construction space. The atlas can show
available road, building, water, land-use and place context where those
sources exist. It cannot replace a site survey or a conversation with the
people whose streets would change.

The catalogue includes original network proposals and alternatives such as
straighter routes or ring forms. Those variants invite comparison of reach,
length and service, not a beauty contest between drawings. A straighter line
may be faster but miss a useful destination. A ring can improve transfers
while requiring more guideway and more complicated operating patterns.
Every alternative needs a stated passenger purpose and a realistic access
route to its stations.

## Move from map to service

Open the service view after understanding the line. Station spacing, dwell,
headway and speed assumptions influence journey time, fleet and energy. A
train that carries 276 named places at a two-minute interval offers 8,280
places per hour by arithmetic, but an actual timetable also requires
protected separation, terminals, boarding time, maintenance and spare
trains. The atlas can calculate planning relationships. It cannot measure
demand that has not been observed or prove a safe operating headway.

One useful exercise is to compare a city-centre segment with a longer outer
segment. Short walks near the centre may justify more stops; an outer line
may place greater value on travel time. A single vehicle type is not
automatically the lowest-cost service on both. The city result should make
such trade-offs visible in offered places, fleet, energy and station scope.

## Understand the two kinds of edit

The planning workspace can prepare route, stop, service and origin–destination
proposals. A planning handoff preserves those proposals and their source
context; it is not itself a calculated railway study. A calculated atlas
study, by contrast, has evaluated service, fleet, civil and cost under a
declared candidate and assumptions. This difference matters when a reader
sees an edited map: moving a marker is not the same event as recalculating a
complete project.

The published v0.6.1 release demonstrates a bounded fresh Samawah
calculation and includes a retained read-only Baghdad comparison. It does
**not** include a native RustGIS
export-and-return journey from the atlas. That route is held at the release
because two source publications do not match. Later v0.7 development has
worked on the return path; it should not be retroactively attributed to
the fixed v0.6.1 package.

## Read the cost view as a question list

Fourteen cost scopes help a reader ask where a proposed railway's resources
would go. They connect vehicle, structures, stations, power, construction,
fleet, staffing, energy, maintenance, renewal and eventual disposal. The
atlas's low, base and high cases are conditional estimates. A city should
identify transferred rates, missing utility diversions, uncertain ground
and unpriced assets before treating any value as a budget.

The most productive atlas session ends with a shortlist of decisions and
evidence requests: which corridor deserves a survey, which station needs an
access study, which service assumption dominates fleet cost, and which local
price or ground condition could change the preferred option. The catalogue
covers 266 cities, but that breadth is a library of planning prompts, not
266 independent construction packages.

## Invite local correction

An open atlas should be easy to challenge. A resident may point out a
barrier that a map misses, an interchange that works poorly at night or
an entrance location that is unsafe in summer heat. A local engineer may
know where utilities, flooding or construction access constrain a neat
line. Such information belongs as a named revision or source, so the
original proposal remains understandable and the new one can be tested.
The project gains more from a corrected station and an honest uncertainty
range than from a catalogue that appears complete but cannot explain
how its choices were made.
