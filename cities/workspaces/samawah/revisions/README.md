# Samawah Design Revisions

OSR City Studio writes deterministic candidate revision JSON files here only
when a user selects **Materialize revision**. Autosaves and map movements do
not create Git history by themselves.

Review a candidate in a branch, commit the project inputs and revision file,
then submit a pull request. After approval, tag the merge using the prefix
`city/samawah/design/` declared in `project.osr.toml`.

The regenerated core alignment uses new station positions and IDs. The older
revision JSON and reviews remain historical records; they do not approve the
current candidate. Previous platform locks are retained separately in
`../network/historical-pre-core-overrides.toml` and are inactive.

The current source lock adopts the 5 October local civil-cost correction on
the retained alignment. Earlier revision source hashes and approval records
are unchanged; they do not approve the corrected candidate. Compile and
validate the current project before reviewing any new revision.
