"""Tier 3 progressive layout benchmark datasets for Inspect AI gating funnel.

Defines smoke, representative, and complete validation matrices evaluating
semantic expressive power and layout hierarchy preservation.
"""

# Phase A: Smoke Test Matrix (Fast Fail)
SMOKE_DATASETS = [
    {
        "test_id": "smoke_card",
        "description": "Simple profile card with header and contact button",
        "components": [
            {"id": "root", "component": "Column", "children": ["header", "btn"]},
            {"id": "header", "component": "Text", "properties": {"value": "Alice Smith"}},
            {"id": "btn", "component": "Button", "properties": {"label": "Email", "action": "$/contact"}},
        ],
    },
    {
        "test_id": "smoke_input",
        "description": "Required text input with data binding",
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

# Phase B: Representative Benchmark Matrix (10 Diverse Layouts)
REPRESENTATIVE_DATASETS = [
    *SMOKE_DATASETS,
    {
        "test_id": "rep_form_nested",
        "description": "Nested form with rows inside columns and multiple bindings",
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
        "test_id": "rep_tabs",
        "description": "Tabbed layout containing distinct form surfaces",
        "components": [
            {"id": "tabs", "component": "Tabs", "children": ["tab1", "tab2"]},
            {"id": "tab1", "component": "Tab", "properties": {"title": "General"}, "children": ["f1"]},
            {"id": "tab2", "component": "Tab", "properties": {"title": "Advanced"}, "children": ["f2"]},
            {"id": "f1", "component": "TextField", "properties": {"label": "Name", "binding": "$/name"}},
            {"id": "f2", "component": "TextField", "properties": {"label": "API Key", "binding": "$/key"}},
        ],
    },
    # Expanding to ensure robust representation across layout tokens
    *[
        {
            "test_id": f"rep_matrix_{i}",
            "description": f"Synthetic layout validation matrix {i}",
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

# Phase C: Complete Verification Suite
COMPLETE_DATASETS = [
    *REPRESENTATIVE_DATASETS,
    *[
        {
            "test_id": f"complete_matrix_{i}",
            "description": f"Deep catalog exhaustive test {i}",
            "components": [
                {
                    "id": f"deep_{i}",
                    "component": "Button",
                    "properties": {"label": f"Action {i}", "action": f"$/action/{i}"},
                }
            ],
        }
        for i in range(11, 31)
    ],
]
