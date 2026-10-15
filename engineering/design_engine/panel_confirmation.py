"""Flat panel mesh, attachment-loss and pressure-holdout confirmation.

All numerical inputs and solve calls are preserved from the common adapter.
Joint capacity and complete installation remain separate qualification checks.
"""


def confirm(result, charge, folder, *, set_check):
    data = result["definition"]
    from engineering.panel_response.plate import solve, single_clip_envelope

    model = data["contract"]
    charge(2, "mesh-refinement")
    coarse = solve(model, mesh_size=0.08)
    fine = solve(model, mesh_size=0.04)
    delta = abs(coarse["maximum_deflection_m"] / fine["maximum_deflection_m"] - 1)
    set_check(
        result,
        "mesh_refinement",
        "passed" if delta < 0.03 else "failed",
        "mapped plate/rail mesh comparison",
        relative_difference=delta,
        limit=0.03,
    )
    set_check(
        result,
        "nominal_deflection",
        fine["deflection_screen"],
        "detailed trimmed MITC4 plate with actual hollow rails and clip locations",
        value=fine["maximum_deflection_m"],
        unit="m",
        limit=0.005,
    )
    charge(len(fine["attachments"]) + 1, "single-attachment-envelope")
    envelope = single_clip_envelope(model, mesh_size=0.04)
    worst = envelope["worst"]
    fault = worst["failed_clip"]
    unstable = worst["status"] == "unstable"
    set_check(
        result,
        "single_attachment_loss",
        "failed" if unstable or worst["maximum_deflection_m"] > 0.005 else "passed",
        "every individual physical clip removed; unstable cases retained",
        case_count=envelope["case_count"],
        governing_case=fault,
    )
    charge(3, "independent-holdouts")
    holdout = solve(model, mesh_size=0.04, pressure_pa=3500)
    combined = (
        dict(
            deflection_screen="failed",
            maximum_deflection_m=None,
            status="outside-domain",
            basis="governing clip loss is unstable; combined linear solution unavailable",
        )
        if unstable
        else solve(model, mesh_size=0.04, pressure_pa=3500, failed_clip=fault)
    )
    soft = solve(model, mesh_size=0.04, clip_stiffness_factor=0.1)
    set_check(
        result,
        "combined_pressure_fault",
        combined["deflection_screen"],
        "independent 3.5 kPa pressure plus governing single-clip loss",
        value=combined["maximum_deflection_m"],
        unit="m",
        governing_case=fault,
        pressure_pa=3500,
    )
    data["confirmation"] = dict(
        coarse=coarse,
        refined=fine,
        all_clip_losses=envelope,
        holdout=holdout,
        combined=combined,
        soft_joint=soft,
    )
    result["metrics"].update(
        detailed_deflection_m=fine["maximum_deflection_m"],
        combined_holdout_deflection_m=combined["maximum_deflection_m"],
    )
    return result
