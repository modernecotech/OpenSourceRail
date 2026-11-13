# CAD and engineering views

The drawings and three-dimensional views make the proposed railway easier
to understand. They show where a wheel bogie sits, how a body shell could
be assembled, where doors and seats might fit, and how a beam could be
handled at a construction site. The v0.6.1 package includes rotatable
geometry and editable examples, alongside pictures meant only to explain
a concept. A reader should ask which kind of image is being shown before
drawing a conclusion from it.

## Look beyond the attractive rendering

A concept rendering can make the passenger journey tangible. It can show a
bright cabin, a compact elevated station or a precast beam being lifted
into place. Its purpose is communication. It does not establish exact
clearances, material thickness, structural strength, access for maintenance
or a safe erection method. A CAD model can carry more geometry, but it too
may omit fasteners, wiring, cooling, seals and working envelopes. A
finite-element model can test a declared load and support condition, while
leaving real joints or material behaviour uncertain.

The engineering gallery provides models of vehicles, bogies, doors,
couplings, launch equipment and guideway elements. Some can be rotated in
a simple viewer; others can be opened in editable CAD software. These
formats serve different readers. A lightweight 3D view is useful for
orientation. An editable solid is useful for testing dimensions and
revisions. An analysis mesh or solver result is useful only when its load,
boundary and material definitions are known.

## Follow one component through the views

Take a passenger door. The cabin image shows how people might board. The
vehicle model locates the opening in the body. The parts proposal breaks
one operator into header, guide, carriage, drive, belt, leaves, seals,
sensors, wiring and fixings. A detailed assembly would then show how
these parts mate, how the leaves move and how a maintainer removes the
guide. The v0.6.1 views and part definitions support the early stages;
they do not close every mating datum, tolerance or removal path.

The same progression applies to a precast span. A picture shows its
place in the city. A CAD solid establishes a proposed shape. An analysis
model applies axle and environmental loads. The build design must still
specify reinforcement or prestress, joints, bearings, piers, foundations,
lifting points and temporary stability. Agreement between two solvers
on an idealized beam cannot fill those gaps.

## What a file format tells you

Rotatable STL and coloured GLB files can communicate geometry efficiently.
Editable STEP and FreeCAD assets make it possible to inspect and change
selected solids. IFC records can connect a geometry model to a construction
or building-information context. The presence of a file in any of these
formats says little by itself about whether every installed component is
counted or whether the model is fit for manufacture. Some exports can
lose source or material metadata; a companion engineering record may be
needed to retain the meaning of a solid.

The release includes optional native-tool examples and comparisons using
SolidCraft and FieldCraft, with independent FreeCAD and CalculiX routes
where recorded. Their support is limited to the stated model domains and
available tool versions. A reader can use them to see how a question was
examined, not to infer that the whole train or guideway has passed a
universal finite-element check.

Good visual review is therefore active. Ask what is missing, whether
maintenance clearance is shown, how forces reach the ground, and whether
the displayed vehicle and station are the same candidate as the quoted
cost. A beautiful picture is most valuable when it helps someone find
the next practical engineering question.

## Use a view to plan maintenance

A model is especially valuable when it shows the space needed to remove
and replace a part. A battery that fits under the floor may still be
impossible to lift out with the bogie installed. A door guide may have
room to operate but too little straight clearance to be extracted. A
cabinet on a station platform may obstruct safe access to a drive. These
questions can be asked while the design is still cheap to change.

The published models therefore belong in conversations with workshop,
construction and maintenance teams as well as analysts. Their comments
can reveal missing fixings, tools, lifting points or inspection surfaces.
The next revision should carry those physical changes into mass, cost
and service planning, not only into a more polished rendering.
