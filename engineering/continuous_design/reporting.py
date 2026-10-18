"""Small operational dashboard, separate from experiment-count claims."""
from datetime import datetime,timezone
import time


def dashboard(status):
    counts=status["research"]["counts"]
    lines=["OpenSourceRail research runner", "State: "+status["runtime"].get("state","unknown")+
        f" | heartbeat age: {status['heartbeat_age_seconds']:.1f}s", "",
        "Lane           Evaluated  Queued  Deferred  Running  Execution errors"]
    for lane,row in status["lanes"].items():
        lines.append(f"{lane:14} {row['completed']:9} {row['queued']:7} {row['deferred']:9} {row['running']:8} {row['error']:17}")
    lines.extend(["", "Evidence categories overlap; passing means the declared checks only."])
    for name,value in counts.items():
        lines.append(f"{name.replace('_',' ')}: {value}")
    latest=status["research"]["last_useful_improvement_unix"]
    lines.extend(["", "Last useful improvement: "+(datetime.fromtimestamp(latest,timezone.utc).isoformat() if latest else "none recorded"),
        "Oldest waiting task age: "+(f"{time.time()-status['oldest_waiting_unix']:.0f}s" if status["oldest_waiting_unix"] else "none"),
        "AI call states: "+str(status["provider_states"]), "Follow-up outbox: "+str(status["outbox_states"]),
        "Workspace output: "+str(status["runtime"].get("used_bytes",0))+" bytes", "",
        "Research champions:"])
    for champion in status["research"]["champions"]:
        lines.append("  "+champion["context"]+" "+champion["key"][:16]+" — "+champion["reason"])
    lines.append("Blocked capabilities:")
    for need in status["blocked_capabilities"]:
        lines.append("  "+need["lane"]+": "+need["item_id"][:160])
    lines.append("Manufacturing and physical release remain open.")
    return "\n".join(lines)
