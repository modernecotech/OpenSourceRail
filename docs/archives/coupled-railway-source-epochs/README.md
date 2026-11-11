# Coupled railway source epoch

This archive retains the exact `engineering/station_rail/braking.py` bytes
required to verify coupled publication
`4363503c0647f6e0aff2253b4c714e4f00d47827722d8fe3e0f6c1fe18c6f91f`. Those
bytes are pinned to commit `dbb62c6aeb48377cb57a00521075bba333f741d2` and have
SHA-256 `905af0b5762a1acf987a831d588f5b8b26f0b400f3bf33be2dac2f940ce38510`.

The published packet stays byte-for-byte unchanged. Its results were not
recalculated after the wheel-inertia implementation changed; the archive only
allows integrity verification under the packet's original source identity.
This does not admit the packet to the current evaluator or qualify its
engineering results.

Run `python -m engineering.station_rail.retired_station_reference verify` to
check this retained source, the coupled packet, and the fixed retired reference.
The result reports `active_packet_source_epochs.coupled-railway` as
`historical` and keeps all physical and release flags false.
