"""Tier 3 progressive layout benchmark datasets for Inspect AI gating funnel.

Defines smoke, representative, and complete validation matrices evaluating
semantic expressive power, feature modularization, and layout hierarchy preservation.
"""

# Phase A: Smoke Test Matrix (Fast Fail)
SMOKE_DATASETS = [
    {
        "test_id": "smoke_card",
        "description": "Simple profile card with header and contact button",
        "required_features": ["layout", "actions"],
        "components": [
            {"id": "root", "component": "Column", "children": ["header", "btn"]},
            {"id": "header", "component": "Text", "properties": {"value": "Alice Smith"}},
            {"id": "btn", "component": "Button", "properties": {"label": "Email", "action": "$/contact"}},
        ],
    },
    {
        "test_id": "smoke_input",
        "description": "Required text input with data binding",
        "required_features": ["layout", "bindings"],
        "components": [
            {
                "id": "field",
                "component": "TextField",
                "properties": {
                    "label": "Username",
                    "binding": "$/user/name",
                    "validation": {"required": True},
                },
            }
        ],
    },
]

# Phase B: Representative Benchmark Matrix (Covers All A2UI Features)
REPRESENTATIVE_DATASETS = [
    *SMOKE_DATASETS,
    {
        "test_id": "rep_form_nested",
        "description": "Nested form with rows inside columns and multiple bindings",
        "required_features": ["layout", "bindings"],
        "components": [
            {"id": "root", "component": "Column", "children": ["title", "row_fields"]},
            {"id": "title", "component": "Text", "properties": {"value": "Deal Submission"}},
            {"id": "row_fields", "component": "Row", "children": ["valField", "dateField"]},
            {
                "id": "valField",
                "component": "TextField",
                "properties": {"label": "Amount", "binding": "$/deal/val", "type": "number"},
            },
            {
                "id": "dateField",
                "component": "TextField",
                "properties": {"label": "Close Date", "binding": "$/deal/date", "type": "date"},
            },
        ],
    },
    {
        "test_id": "rep_accessibility",
        "description": "Accessible surface with screen reader metadata",
        "required_features": ["layout", "accessibility"],
        "components": [
            {
                "id": "root",
                "component": "Card",
                "accessibility": {"label": "Important Alert", "description": "System notification"},
                "children": ["msg"],
            },
            {"id": "msg", "component": "Text", "properties": {"value": "Update required"}},
        ],
    },
    {
        "test_id": "rep_full_interactive",
        "description": "Full interactive view combining actions, bindings, and layout weighting",
        "required_features": ["layout", "actions", "bindings", "weight"],
        "components": [
            {
                "id": "root",
                "component": "Row",
                "children": ["left", "right"],
            },
            {"id": "left", "component": "Text", "weight": 1, "properties": {"value": "Status"}},
            {"id": "right", "component": "Button", "weight": 2, "properties": {"label": "Sync", "action": "$/sync"}},
        ],
    },
    *[
        {
            "test_id": f"rep_matrix_{i}",
            "description": f"Synthetic layout validation matrix {i}",
            "required_features": ["layout", "bindings"],
            "components": [
                {
                    "id": f"comp_{i}",
                    "component": "TextField",
                    "properties": {"label": f"Field {i}", "binding": f"$/path/{i}"},
                }
            ],
        }
        for i in range(5, 11)
    ],
]

# Phase C: Complete Verification Suite (Training Partition)
COMPLETE_DATASETS = [
    *REPRESENTATIVE_DATASETS,
    *[
        {
            "test_id": f"complete_matrix_{i}",
            "description": f"Deep catalog exhaustive test {i}",
            "required_features": ["layout", "actions"],
            "components": [
                {
                    "id": f"deep_{i}",
                    "component": "Button",
                    "properties": {"label": f"Action {i}", "action": f"$/action/{i}"},
                }
            ],
        }
        for i in range(11, 25)
    ],
]

# Phase D: Held-Back Holdout Validation Suite
VALIDATION_DATASETS = [
    *[
        {
            "test_id": f"validation_matrix_{i}",
            "description": f"Held-back holdout generalization verification {i}",
            "required_features": ["layout", "actions", "bindings", "accessibility"],
            "components": [
                {
                    "id": f"holdout_{i}",
                    "component": "Card",
                    "accessibility": {"label": f"Card {i}", "description": "Validation holdout"},
                    "children": ["btn"],
                },
                {
                    "id": "btn",
                    "component": "Button",
                    "properties": {"label": "Execute", "action": f"$/execute/{i}"},
                },
            ],
        }
        for i in range(25, 31)
    ],
]
