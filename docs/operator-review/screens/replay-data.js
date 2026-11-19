const supervisionReplay = {
  "candidate": "osr-v07-joined-civil-518dad57a3af5046f40c8f4f",
  "evaluation": "9ec5da2aee867713db388e7b64fceedd25ead65ea169370ef6e521d29aaf71df",
  "frames": [
    {
      "name": "Normal readings",
      "rows": [
        {
          "active": false,
          "asset": "station-01",
          "occurrences": 0,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "station-dispatch-controller",
          "source_time": "08:00:00",
          "value": 0.0
        },
        {
          "active": false,
          "asset": "section-01",
          "occurrences": 0,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "section-control-gateway",
          "source_time": "08:00:00",
          "value": 0.0
        },
        {
          "active": false,
          "asset": "grid-01",
          "occurrences": 0,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "grid-protection-gateway",
          "source_time": "08:00:00",
          "value": 0.0
        }
      ],
      "time": "08:00:00"
    },
    {
      "name": "Section trips",
      "rows": [
        {
          "active": false,
          "asset": "station-01",
          "occurrences": 0,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "station-dispatch-controller",
          "source_time": "08:00:05",
          "value": 0.0
        },
        {
          "active": true,
          "asset": "section-01",
          "occurrences": 1,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "section-control-gateway",
          "source_time": "08:00:05",
          "value": 1.0
        },
        {
          "active": false,
          "asset": "grid-01",
          "occurrences": 0,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "grid-protection-gateway",
          "source_time": "08:00:05",
          "value": 0.0
        }
      ],
      "time": "08:00:05"
    },
    {
      "name": "Section signal stale",
      "rows": [
        {
          "active": false,
          "asset": "station-01",
          "occurrences": 0,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "station-dispatch-controller",
          "source_time": "08:00:38",
          "value": 0.0
        },
        {
          "active": true,
          "asset": "section-01",
          "occurrences": 1,
          "quality": "stale",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "section-control-gateway",
          "source_time": "08:00:05",
          "value": null
        },
        {
          "active": false,
          "asset": "grid-01",
          "occurrences": 0,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "grid-protection-gateway",
          "source_time": "08:00:38",
          "value": 0.0
        }
      ],
      "time": "08:00:38"
    },
    {
      "name": "Signal restored and trip cleared",
      "rows": [
        {
          "active": false,
          "asset": "station-01",
          "occurrences": 0,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "station-dispatch-controller",
          "source_time": "08:00:40",
          "value": 0.0
        },
        {
          "active": false,
          "asset": "section-01",
          "occurrences": 1,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "section-control-gateway",
          "source_time": "08:00:40",
          "value": 0.0
        },
        {
          "active": false,
          "asset": "grid-01",
          "occurrences": 0,
          "quality": "valid",
          "response": "Inspect the protected local system; this display cannot reset it",
          "role": "grid-protection-gateway",
          "source_time": "08:00:40",
          "value": 0.0
        }
      ],
      "time": "08:00:40"
    }
  ],
  "package": "18c7d86cf4af728f765d5ff528c91400cc86d4610b86a712f8e68b56ab9f0faa"
};
