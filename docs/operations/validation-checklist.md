# Operations Validation Checklist

The rulebook is drafted in English. It becomes deployment-ready only
after operator and authority review. This checklist defines the review
evidence expected for v0.2/v2.1.

| Gate | Required evidence | Closure criterion |
|---|---|---|
| Operator workshop | Dispatcher, maintenance, station, control-centre, and emergency-service walkthrough notes | Every rule block has accepted, changed, or rejected status |
| Local authority adaptation | Regulator comments, required terminology, incident reporting law, police/medical/fire contact protocol | Local deviations are documented without weakening safety requirements |
| Training package | Role syllabus, practical drills, assessment form, recurrent interval, competence matrix | Staff competence evidence can be linked from certification §8.3 |
| Simulation drills | Degraded mode, fire, passenger incident, intrusion, point failure, comms loss, station evacuation | Drill outcomes map to rule IDs and simulator scenarios |
| Translation if needed | Country-language rulebook and controlled terminology table | English remains canonical; translation is reviewed by operator and safety assessor |
| Handover to OCC tooling | Console action labels, alarm names, incident categories, and audit-log fields align with rule text | GUI/live-system terminology no longer diverges from the rulebook |

Legacy driver-rule files remain for GoA 2/cabbed variants. GoA 4
deployments close this checklist against dispatcher, station,
maintenance, and control-centre roles.
