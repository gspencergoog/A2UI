# Component Gallery

This page showcases all A2UI components with examples and usage patterns.

=== "v0.8"

    For the complete technical specification, see the [Standard Catalog Definition](https://a2ui.org/specification/v0_8/standard_catalog_definition.json).

=== "v0.9"

    For the complete technical specification, see the [Basic Catalog Definition](https://a2ui.org/specification/v0_9/basic_catalog.json).

## Layout Components

### Row

Horizontal layout container. Children are arranged left-to-right.

=== "v0.8"

    ```json
    {
      "id": "toolbar",
      "component": {
        "Row": {
          "children": { "explicitList": ["btn1", "btn2", "btn3"] },
          "alignment": "center"
        }
      }
    }
    ```

    **Properties:**

    - `children`: Static array (`explicitList`) or dynamic `template`
    - `distribution`: `start`, `center`, `end`, `spaceBetween`, `spaceAround`, `spaceEvenly`
    - `alignment`: `start`, `center`, `end`, `stretch`

=== "v0.9"

    ```json
    {
      "id": "toolbar",
      "component": "Row",
      "children": ["btn1", "btn2", "btn3"],
      "align": "center"
    }
    ```

    **Properties:**

    - `children`: Array of component IDs, or a template object for dynamic lists
    - `justify`: `start`, `center`, `end`, `spaceBetween`, `spaceAround`, `spaceEvenly`, `stretch`
    - `align`: `center`, `start`, `end`, `stretch`, `baseline`

### Column

Vertical layout container. Children are arranged top-to-bottom.

=== "v0.8"

    ```json
    {
      "id": "content",
      "component": {
        "Column": {
          "children": { "explicitList": ["header", "body", "footer"] }
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "content",
      "component": "Column",
      "children": ["header", "body", "footer"]
    }
    ```

### List

Scrollable list of items.

=== "v0.8"

    ```json
    {
      "id": "message-list",
      "component": {
        "List": {
          "children": {
            "template": {
              "dataBinding": "/messages",
              "componentId": "message-item"
            }
          }
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "message-list",
      "component": "List",
      "children": {
        "componentId": "message-item",
        "path": "/messages"
      }
    }
    ```

## Display Components

### Text

Display text content with optional styling.

=== "v0.8"

    ```json
    {
      "id": "title",
      "component": {
        "Text": {
          "text": { "literalString": "Welcome to A2UI" },
          "usageHint": "h1"
        }
      }
    }
    ```

    **`usageHint` values:** `h1`, `h2`, `h3`, `h4`, `h5`, `caption`, `body`

=== "v0.9"

    ```json
    {
      "id": "title",
      "component": "Text",
      "text": "Welcome to A2UI",
      "variant": "h1"
    }
    ```

    **`variant` values:** `h1`, `h2`, `h3`, `h4`, `h5`, `caption`, `body`

### Image

Display images from URLs.

=== "v0.8"

    ```json
    {
      "id": "logo",
      "component": {
        "Image": {
          "url": { "literalString": "https://example.com/logo.png" }
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "logo",
      "component": "Image",
      "url": "https://example.com/logo.png"
    }
    ```

### Icon

Display icons using Material Icons or custom icon sets.

=== "v0.8"

    ```json
    {
      "id": "check-icon",
      "component": {
        "Icon": {
          "name": { "literalString": "check" }
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "check-icon",
      "component": "Icon",
      "name": "check"
    }
    ```

### Divider

Visual separator line.

=== "v0.8"

    ```json
    {
      "id": "separator",
      "component": {
        "Divider": {
          "axis": "horizontal"
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "separator",
      "component": "Divider",
      "axis": "horizontal"
    }
    ```

## Interactive Components

### Button

Clickable button with action support.

=== "v0.8"

    ```json
    {
      "id": "submit-btn",
      "component": {
        "Button": {
          "child": "submit-text",
          "primary": true,
          "action": { "name": "submit_form" }
        }
      }
    }
    ```

    **Properties:**

    - `child`: ID of the component to display inside the button
    - `primary`: Boolean for primary action styling
    - `action`: Action to perform on click

=== "v0.9"

    ```json
    {
      "id": "submit-btn",
      "component": "Button",
      "child": "submit-text",
      "variant": "primary",
      "action": {
        "event": { "name": "submit_form" }
      }
    }
    ```

    **Properties:**

    - `child`: ID of the component to display inside the button
    - `variant`: `primary`, `secondary`, etc.
    - `action`: Action with structured event format

### TextField

Text input field.

=== "v0.8"

    ```json
    {
      "id": "email-input",
      "component": {
        "TextField": {
          "label": { "literalString": "Email Address" },
          "text": { "path": "/user/email" },
          "textFieldType": "shortText"
        }
      }
    }
    ```

    **`textFieldType` values:** `date`, `longText`, `number`, `shortText`, `obscured`

=== "v0.9"

    ```json
    {
      "id": "email-input",
      "component": "TextField",
      "label": "Email Address",
      "value": { "path": "/user/email" },
      "textFieldType": "shortText"
    }
    ```

    **`textFieldType` values:** `date`, `longText`, `number`, `shortText`, `obscured`

### CheckBox

Boolean toggle.

=== "v0.8"

    ```json
    {
      "id": "terms-checkbox",
      "component": {
        "CheckBox": {
          "label": { "literalString": "I agree to the terms" },
          "value": { "path": "/form/agreedToTerms" }
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "terms-checkbox",
      "component": "CheckBox",
      "label": "I agree to the terms",
      "value": { "path": "/form/agreedToTerms" }
    }
    ```

### Slider

Numeric range input.

=== "v0.8"

    ```json
    {
      "id": "volume",
      "component": {
        "Slider": {
          "value": { "path": "/settings/volume" },
          "minValue": 0,
          "maxValue": 100
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "volume",
      "component": "Slider",
      "value": { "path": "/settings/volume" },
      "minValue": 0,
      "maxValue": 100
    }
    ```

### DateTimeInput

Date and/or time picker.

=== "v0.8"

    ```json
    {
      "id": "date-picker",
      "component": {
        "DateTimeInput": {
          "value": { "path": "/booking/date" },
          "enableDate": true,
          "enableTime": false
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "date-picker",
      "component": "DateTimeInput",
      "value": { "path": "/booking/date" },
      "enableDate": true,
      "enableTime": false
    }
    ```

### ChoicePicker

Select one or more options from a list. (Called `MultipleChoice` in v0.8.)

=== "v0.8"

    ```json
    {
      "id": "country-select",
      "component": {
        "MultipleChoice": {
          "options": [
            { "label": { "literalString": "USA" }, "value": "us" },
            { "label": { "literalString": "Canada" }, "value": "ca" },
            { "label": { "literalString": "UK" }, "value": "uk" }
          ],
          "selections": { "path": "/form/country" },
          "maxAllowedSelections": 1
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "country-select",
      "component": "ChoicePicker",
      "options": [
        { "label": "USA", "value": "us" },
        { "label": "Canada", "value": "ca" },
        { "label": "UK", "value": "uk" }
      ],
      "selections": { "path": "/form/country" },
      "maxAllowedSelections": 1
    }
    ```

## Container Components

### Card

Container with elevation/border and padding.

=== "v0.8"

    ```json
    {
      "id": "info-card",
      "component": {
        "Card": {
          "child": "card-content"
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "info-card",
      "component": "Card",
      "child": "card-content"
    }
    ```

### Modal

Overlay dialog.

=== "v0.8"

    ```json
    {
      "id": "confirmation-modal",
      "component": {
        "Modal": {
          "entryPointChild": "open-modal-btn",
          "contentChild": "modal-content"
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "confirmation-modal",
      "component": "Modal",
      "entryPointChild": "open-modal-btn",
      "contentChild": "modal-content"
    }
    ```

### Tabs

Tabbed interface.

=== "v0.8"

    ```json
    {
      "id": "settings-tabs",
      "component": {
        "Tabs": {
          "tabItems": [
            {
              "title": { "literalString": "General" },
              "child": "general-settings"
            },
            {
              "title": { "literalString": "Privacy" },
              "child": "privacy-settings"
            },
            {
              "title": { "literalString": "Advanced" },
              "child": "advanced-settings"
            }
          ]
        }
      }
    }
    ```

=== "v0.9"

    ```json
    {
      "id": "settings-tabs",
      "component": "Tabs",
      "tabItems": [
        { "title": "General", "child": "general-settings" },
        { "title": "Privacy", "child": "privacy-settings" },
        { "title": "Advanced", "child": "advanced-settings" }
      ]
    }
    ```

## Common Properties

Most components support these common properties:

- `id` (required): Unique identifier for the component instance
- `accessibility`: Accessibility attributes (label, role)

=== "v0.8"

    - `weight`: Flex-grow value when inside a Row or Column (specified alongside `id` and `component`)

=== "v0.9"

    - `weight`: Flex-grow value when inside a Row or Column (top-level property on the component)

## Live Examples

To see all components in action, run the component gallery demo:

```bash
cd samples/client/angular
npm start -- gallery
```

This launches a live gallery with all components, their variations, and interactive examples.

## Further Reading

=== "v0.8"

    - **[Standard Catalog Definition](https://a2ui.org/specification/v0_8/standard_catalog_definition.json)**: Complete v0.8 component schemas
    - **[Custom Components Guide](../guides/custom-components.md)**: Build your own components
    - **[Theming Guide](../guides/theming.md)**: Style components to match your brand

=== "v0.9"

    - **[Basic Catalog Definition](https://a2ui.org/specification/v0_9/basic_catalog.json)**: Complete v0.9 component schemas
    - **[Custom Components Guide](../guides/custom-components.md)**: Build your own components
    - **[Theming Guide](../guides/theming.md)**: Style components to match your brand
