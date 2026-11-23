"""Draw the six-station quotation circuit from the verified commissioning report."""

from html import escape

from engineering.outline.baghdad_system import _id


def parallel_svg(report):
    if report["evaluation_id"] != _id({k: v for k, v in report.items() if k != "evaluation_id"}):
        raise ValueError("Commissioning report has changed")
    p = report["parallel_quotation"]
    scope = p["scope"]
    design = scope["design"]
    if scope["design_id"] != _id(design) or scope["option"] != "six_site_parallel":
        raise ValueError("Expected the paired Airport circuit")
    sites = design["site_chainage_km"]
    qty = p["quantity_enquiry"]
    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 640" role="img" aria-labelledby="title desc">',
        '<title id="title">Six-station Airport supply quotation</title>',
        '<desc id="desc">Six rectifier sites share a two-track radial layout. One restored circuit detail shows two positive paths and two returns connected inside one breaker zone.</desc>',
        '<rect width="1040" height="640" fill="white"/>',
        "<style>text{font:17px sans-serif;fill:#183246}.title{font:bold 30px sans-serif}.label{font:bold 19px sans-serif}.small{font:14px sans-serif}.id{font:12px monospace}.pos,.neg{fill:none;stroke:#126678;stroke-width:3}.neg{stroke:#79543c;stroke-dasharray:7 3}.unit{fill:#edf6f7;stroke:#266477;stroke-width:2}</style>",
    ]

    def label(x, y, message, style="", anchor="start"):
        elements.append(
            f'<text x="{x}" y="{y}" class="{style}" text-anchor="{anchor}">{escape(message)}</text>'
        )

    label(28, 43, "Six-station supply quotation", "title")
    label(28, 73, "12 km Airport line · paired conductors and returns · independent station rectifiers")
    label(28, 106, "Rectifier sites along the operating route", "label")
    elements.append('<path class="pos" d="M75 147H965"/>')
    for i, site in enumerate(sites):
        x = 75 + 890 * site / design["route_km"]
        elements.append(f'<rect x="{x-28}" y="132" width="56" height="29" rx="4" class="unit"/>')
        label(x, 153, f"S{i+1:02d}", "small", "middle")
        label(x, 184, f"{site:.1f} km", "small", "middle")
    label(28, 221, "One restored traction zone, shown as an equivalent circuit", "label")
    label(
        28,
        248,
        "Each branch remains within the same insulated section. Positive paths share one protected outgoing circuit.",
    )
    elements += [
        '<rect x="45" y="303" width="145" height="88" rx="6" class="unit"/>',
        '<rect x="253" y="291" width="82" height="32" class="unit"/>',
        '<rect x="832" y="303" width="147" height="88" rx="6" class="unit"/>',
        '<path class="pos" d="M190 318H223V307H253M335 307H364M364 307V284H725V307M364 307V330H725V307H805V318H832"/>',
        '<path class="neg" d="M832 377H756M756 377V355H385V377M756 377V400H385V377H190"/>',
    ]
    label(118, 342, "Rectifier", "label", "middle")
    label(118, 367, "DC + and −", "small", "middle")
    label(294, 312, "breaker", "small", "middle")
    label(542, 278, "positive longitudinal branch × 2", "small", "middle")
    label(544, 421, "return longitudinal branch × 2", "small", "middle")
    label(907, 340, "Train", "label", "middle")
    label(907, 365, "shoe and return", "small", "middle")
    label(
        28,
        463,
        f'{qty["rectifier_and_transformer_groups"]} source groups · {qty["main_outgoing_breakers"]} outgoing breakers · {qty["track_midpoint_ties"]} normally open ties',
    )
    label(
        28,
        491,
        f'{qty["positive_longitudinal_path_km"]:.0f} positive path-km · {qty["return_longitudinal_path_km"]:.0f} return path-km · {qty["peak_ka_each_branch_with_unproved_sharing"]:.2f} kA peak rating enquiry per branch',
    )
    label(
        28,
        521,
        f'Combined sensitivity with one site out: {p["minimum_combined_collector_kv"]:.4f} kV. With one path pair also lost: {p["single_path_lost_with_site_out_combined"]["collector_kv"]:.4f} kV.',
    )
    label(
        28,
        553,
        "Common shoe, cross-bonds and joints have a 1 mΩ hot allowance. Return thermal and protection evidence.",
    )
    label(28, 590, "Quotation design " + scope["design_id"], "id")
    label(28, 613, "Parent opening " + report["binding"]["opening_candidate_id"], "id")
    elements.append("</svg>")
    return "\n".join(elements)
