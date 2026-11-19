// Generated from quantities.json by capture-workforce.mjs
const workforceStudy = {
  "schema": "osr.factory-workforce.study.1",
  "source_sha256": {
    "cities/Baghdad/system-results.json": "be01359239e9b97efdae45822628688ffb1225a17afd36df136aaffb0928c06e",
    "cities/Baghdad/system.toml": "5a847f9bf78cb1ad0ed81a66136a511cce39a5ee0bc99bb20d35717da848a035",
    "docs/operator-review/delivery/calculate.py": "dad669f43fa2b1d6a661ef106e15a2a8b1a74c6f2f6b51a7d6ab4410dd3e8b57",
    "docs/reference-v07/concept.toml": "033849bb4db3a0b28adb5a345a39601330f5160cd8c100a4dd4b790123485a18",
    "docs/reference-v07/digital/production/handoff.json": "c8f89fd421e9413ddbe6ef4b934c153469b0a87f1ed54d8761a1d57c77512a4c"
  },
  "status": "capacity and quotation study",
  "studies": {
    "core": {
      "civil": {
        "beams": 6000,
        "civil_yard_day_posts": 36,
        "erection_day_posts": 16,
        "erection_fronts": 2,
        "minimum_pre_erection_stock_per_yard": 440,
        "off_yard_slots_needed_per_yard": 260,
        "yards": 2
      },
      "production_day_posts": 202,
      "roster": {
        "duty_hours_per_year": {
          "OCC control, traction, incidents and information": 35040,
          "civil, track and power response": 35040,
          "depot rolling-stock technicians": 58400,
          "planning, payroll, stores and trainers": 10320,
          "station duty and passenger assistance": 236520,
          "station security and cleaning": 157680,
          "train operators": 156220
        },
        "field_groups": 1,
        "posts_fte": {
          "OCC control, traction, incidents and information": 21,
          "civil, track and power response": 21,
          "depot rolling-stock technicians": 34,
          "planning, payroll, stores and trainers": 6,
          "station duty and passenger assistance": 138,
          "station security and cleaning": 92,
          "train operators": 91
        },
        "total_fte": 403,
        "train_operator_hours_per_day": 428
      },
      "source_evaluation_id": "63dbda54f7498fcd3a2e390fe37571fb6049fa39c02f9640fe39e15d70560dbc",
      "source_physical_id": "osr-v07-joined-civil-518dad57a3af5046f40c8f4f",
      "source_selection_id": "osr-v07-digital-design-20261117",
      "vehicle": {
        "cars": 306,
        "cars_capacity": 380,
        "cars_per_line_in_window": 76,
        "direct_content_hours": 220320,
        "direct_content_job_years_at_1720_hours": 128.1,
        "direct_posts_all_lines": 130,
        "direct_posts_by_stage": {
          "HVAC and auxiliaries": 3,
          "body": 9,
          "bogies and drive": 4,
          "doors and interior": 3,
          "marriage and test": 3,
          "wiring, collection and cooling": 4
        },
        "direct_posts_per_line": 26,
        "effective_line_days": 408,
        "first_car_effective_day": 30,
        "hours_per_car_by_stage": {
          "HVAC and auxiliaries": 80,
          "body": 260,
          "bogies and drive": 120,
          "doors and interior": 80,
          "marriage and test": 80,
          "wiring, collection and cooling": 100
        },
        "lines": 5,
        "scheduled_workdays": 480,
        "support_posts_all_lines": 20,
        "takt_effective_days": 5
      }
    },
    "first": {
      "civil": {
        "beams": 29640,
        "civil_yard_day_posts": 108,
        "erection_day_posts": 48,
        "erection_fronts": 6,
        "peak_month_end_total_inventory": 983,
        "slots_per_yard_if_balanced": 164,
        "slots_per_yard_offered": 180,
        "yards": 6
      },
      "production_day_posts": 624,
      "roster": {
        "duty_hours_per_year": {
          "OCC control, traction, incidents and information": 70080,
          "civil, track and power response": 175200,
          "depot rolling-stock technicians": 233600,
          "planning, payroll, stores and trainers": 41280,
          "station duty and passenger assistance": 1261440,
          "station security and cleaning": 840960,
          "train operators": 729270
        },
        "field_groups": 5,
        "posts_fte": {
          "OCC control, traction, incidents and information": 41,
          "civil, track and power response": 102,
          "depot rolling-stock technicians": 136,
          "planning, payroll, stores and trainers": 24,
          "station duty and passenger assistance": 734,
          "station security and cleaning": 489,
          "train operators": 424
        },
        "total_fte": 1950,
        "train_operator_hours_per_day": 1998
      },
      "source_evaluation_id": "12d4630a9c69a023b7c538c6b9a7413b38622697b7c127db6839d89d93170054",
      "source_physical_id": "f6844cd4d9f5d9320fa421b37eb074b9911d3cd695d350fdc464cc3597184a72",
      "vehicle": {
        "cars": 1452,
        "cars_capacity": 1464,
        "cars_per_line_in_window": 122,
        "direct_content_hours": 1452000,
        "direct_content_job_years_at_1720_hours": 844.2,
        "direct_posts_all_lines": 420,
        "direct_posts_by_stage": {
          "HVAC and auxiliaries": 3,
          "body": 9,
          "bogies and drive": 4,
          "doors and interior": 9,
          "marriage and test": 3,
          "wiring, collection and cooling": 7
        },
        "direct_posts_per_line": 35,
        "effective_line_days": 637,
        "first_car_effective_day": 30,
        "hours_per_car_by_stage": {
          "HVAC and auxiliaries": 80,
          "body": 260,
          "bogies and drive": 120,
          "doors and interior": 260,
          "marriage and test": 80,
          "wiring, collection and cooling": 200
        },
        "lines": 12,
        "scheduled_workdays": 750,
        "support_posts_all_lines": 48,
        "takt_effective_days": 5
      }
    },
    "metropolitan": {
      "civil": {
        "beams": 121156,
        "civil_yard_day_posts": 180,
        "erection_day_posts": 80,
        "erection_fronts": 10,
        "peak_month_end_total_inventory": 1638,
        "slots_per_yard_if_balanced": 164,
        "slots_per_yard_offered": 180,
        "yards": 10
      },
      "production_day_posts": 1040,
      "roster": {
        "duty_hours_per_year": {
          "OCC control, traction, incidents and information": 140160,
          "civil, track and power response": 735840,
          "depot rolling-stock technicians": 700800,
          "planning, payroll, stores and trainers": 123840,
          "station duty and passenger assistance": 5518800,
          "station security and cleaning": 3679200,
          "train operators": 2815610
        },
        "field_groups": 21,
        "posts_fte": {
          "OCC control, traction, incidents and information": 82,
          "civil, track and power response": 428,
          "depot rolling-stock technicians": 408,
          "planning, payroll, stores and trainers": 72,
          "station duty and passenger assistance": 3209,
          "station security and cleaning": 2140,
          "train operators": 1637
        },
        "total_fte": 7976,
        "train_operator_hours_per_day": 7714
      },
      "source_evaluation_id": "54c45fc9feb942bd0f63b2d9aaf4688cb794409801793967f047050e61586db3",
      "source_physical_id": "28d1d23756788171634dbf3ac50dbbae0254f4ca9cd5b732821ae9a88635408c",
      "vehicle": {
        "cars": 5604,
        "cars_capacity": 5840,
        "cars_per_line_in_window": 292,
        "direct_content_hours": 5604000,
        "direct_content_job_years_at_1720_hours": 3258.1,
        "direct_posts_all_lines": 700,
        "direct_posts_by_stage": {
          "HVAC and auxiliaries": 3,
          "body": 9,
          "bogies and drive": 4,
          "doors and interior": 9,
          "marriage and test": 3,
          "wiring, collection and cooling": 7
        },
        "direct_posts_per_line": 35,
        "effective_line_days": 1487,
        "first_car_effective_day": 30,
        "hours_per_car_by_stage": {
          "HVAC and auxiliaries": 80,
          "body": 260,
          "bogies and drive": 120,
          "doors and interior": 260,
          "marriage and test": 80,
          "wiring, collection and cooling": 200
        },
        "lines": 20,
        "scheduled_workdays": 1750,
        "support_posts_all_lines": 80,
        "takt_effective_days": 5
      }
    }
  },
  "study_evaluation_sha256": "2f14e0c3ee452126b1537625f301b74a0c932cb11283c5c04e97b2edd927d930"
};
