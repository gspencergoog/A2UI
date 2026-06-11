# A2UI Express Output Contract

You must output the user interface using the compact A2UI Express DSL notation.
You MUST surround the entire A2UI Express DSL block with the sentinel tags `<a2ui>` and `</a2ui>`.

## Grammar Rules

1. Output exactly one variable assignment statement per line:
   variable_name = ComponentName(arg1, arg2, ...)

2. The interface tree must have a single entry point assigned to the reserved variable 'root'.

3. Primitives:
   - Strings: enclose in double quotes, e.g., "label"
   - Numbers: write as integers or decimals, e.g., 42
   - Booleans: write true or false
   - Null values: write null

4. Lists: represent as arrays, e.g., [child1, child2]

5. Data bindings: prefix absolute paths in the data model with '@', e.g., @/user/firstName.
   Prefix relative list scopes with '@', e.g., @firstName.

6. Logic and validation: prefix client check rules with '?', e.g., ?required or
   ?regex("^[0-9]5$").

7. Action events: represent server-side actions using the Event helper:
   Event("save_deal", {rep: @/form/rep})

8. Nested functions: call client functions directly using catalog signatures,
   for example openUrl("https://example.com").

9. Data model population: Assign a value directly to an absolute data path (e.g. @/path/to/key = "value") to populate or initialize values inside the shared dataModel. The value can be a primitive, array, or map.

## Positional Component Signatures

Use these exact positional signatures to instantiate components. Do not output property keys:
• AudioPlayer(url, description?)
  - url: The URL of the audio to be played.
  - description: A description of the audio, such as a title or summary.

• Button(child, variant?, action, checks?)
  - child: The ID of the child component. Use a 'Text' component for a labeled button. Only use an 'Icon' if the requirements explicitly ask for an icon-only button. Do NOT define the child component inline.
  - variant: A hint for the button style. If omitted, a default button style is used. 'primary' indicates this is the main call-to-action button. 'borderless' means the button has no visual border or background, making its child content appear like a clickable link.

• Card(child)
  - child: The ID of the single child component to be rendered inside the card. To display multiple elements, you MUST wrap them in a layout component (like Column or Row) and pass that container's ID here. Do NOT pass multiple IDs or a non-existent ID. Do NOT define the child component inline.

• CheckBox(label, value, checks?)
  - label: The text to display next to the checkbox.
  - value: The current state of the checkbox (true for checked, false for unchecked).

• ChoicePicker(label?, variant?, options, value, displayStyle?, filterable?, checks?)
  A component that allows selecting one or more options from a list.
  - label: The label for the group of options.
  - variant: A hint for how the choice picker should be displayed and behave.
  - options: The list of available options to choose from.
  - value: The list of currently selected values. This should be bound to a string array in the data model.
  - displayStyle: The display style of the component.
  - filterable: If true, displays a search input to filter the options.

• Column(children, justify?, align?)
  A layout component that arranges its children vertically. To create a grid layout, nest Rows within this Column.
  - children: Defines the children. Use an array of strings for a fixed set of children, or a template object to generate children from a data list. Children cannot be defined inline, they must be referred to by ID.
  - justify: Defines the arrangement of children along the main axis (vertically). Use 'spaceBetween' to push items to the edges (e.g. header at top, footer at bottom), or 'start'/'end'/'center' to pack them together.
  - align: Defines the alignment of children along the cross axis (horizontally). This is similar to the CSS 'align-items' property.

• DateTimeInput(value, enableDate?, enableTime?, min?, max?, label?, checks?)
  - value: The selected date and/or time value in ISO 8601 format. If not yet set, initialize with an empty string.
  - enableDate: If true, allows the user to select a date.
  - enableTime: If true, allows the user to select a time.
  - min: The minimum allowed date/time in ISO 8601 format.
  - max: The maximum allowed date/time in ISO 8601 format.
  - label: The text label for the input field.

• Divider(axis?)
  - axis: The orientation of the divider.

• Icon(name)
  - name: The name of the icon to display.

• Image(url, description?, fit?, variant?)
  - url: The URL of the image to display.
  - description: Accessibility text for the image.
  - fit: Specifies how the image should be resized to fit its container. This corresponds to the CSS 'object-fit' property.
  - variant: A hint for the image size and style.

• List(children, direction?, align?)
  - children: Defines the children. Use an array of strings for a fixed set of children, or a template object to generate children from a data list.
  - direction: The direction in which the list items are laid out.
  - align: Defines the alignment of children along the cross axis.

• Modal(trigger, content)
  - trigger: The ID of the component that opens the modal when interacted with (e.g., a button). Do NOT define the component inline.
  - content: The ID of the component to be displayed inside the modal. Do NOT define the component inline.

• Row(children, justify?, align?)
  A layout component that arranges its children horizontally. To create a grid layout, nest Columns within this Row.
  - children: Defines the children. Use an array of strings for a fixed set of children, or a template object to generate children from a data list. Children cannot be defined inline, they must be referred to by ID.
  - justify: Defines the arrangement of children along the main axis (horizontally). Use 'spaceBetween' to push items to the edges, or 'start'/'end'/'center' to pack them together.
  - align: Defines the alignment of children along the cross axis (vertically). This is similar to the CSS 'align-items' property, but uses camelCase values (e.g., 'start').

• Slider(label?, min?, max, value, steps?, checks?)
  - label: The label for the slider.
  - min: The minimum value of the slider.
  - max: The maximum value of the slider.
  - value: The current value of the slider.
  - steps: The number of discrete divisions in the slider range. If specified, the slider will snap to discrete values.

• Tabs(tabs)
  - tabs: An array of objects, where each object defines a tab with a title and a child component.

• Text(text, variant?)
  - text: The text content to display. While simple Markdown formatting is supported (i.e. without HTML, images, or links), utilizing dedicated UI components is generally preferred for a richer and more structured presentation.
  - variant: A hint for the base text style.

• TextField(label, value?, placeholder?, variant?, checks?)
  - label: The text label for the input field.
  - value: The value of the text field.
  - placeholder: The placeholder text for the input field.
  - variant: The type of input field to display.

• Video(url, posterUrl?)
  - url: The URL of the video to display.
  - posterUrl: The URL of the poster image to display before the video plays.

## Positional Function Signatures

Use these exact positional signatures to instantiate check rules or logic functions:
• and(values)
  Performs a logical AND operation on a list of boolean values.
  - values: The list of boolean values to evaluate.

• email(value)
  Checks that the value is a valid email address.

• formatCurrency(value, currency, decimals?, grouping?)
  Formats a number as a currency string.
  - value: The monetary amount.
  - currency: The ISO 4217 currency code (e.g., 'USD', 'EUR').
  - decimals: Optional. The number of decimal places to show. Defaults to 0 or 2 depending on locale.
  - grouping: Optional. If true, uses locale-specific grouping separators (e.g. '1,000'). If false, returns raw digits (e.g. '1000'). Defaults to true.

• formatDate(value, format)
  Formats a timestamp into a string using a pattern.
  - value: The date to format.
  - format: A Unicode TR35 date pattern string.

• formatNumber(value, decimals?, grouping?)
  Formats a number with the specified grouping and decimal precision.
  - value: The number to format.
  - decimals: Optional. The number of decimal places to show. Defaults to 0 or 2 depending on locale.
  - grouping: Optional. If true, uses locale-specific grouping separators (e.g. '1,000'). If false, returns raw digits (e.g. '1000'). Defaults to true.

• formatString(value)
  Performs string interpolation of data model values and other functions in the catalog functions list and returns the resulting string. The value string can contain interpolated expressions in the `${expression}` format. Supported expression types include: JSON Pointer paths to the data model (e.g., `${/absolute/path}` or `${relative/path}`), and client-side function calls (e.g., `${now()}`). Function arguments must be named (e.g., `${formatDate(value:${/currentDate}, format:'MM-dd')}`). To include a literal `${` sequence, escape it as `\${`.

• length(value, min?, max?)
  Checks string length constraints.
  - min: The minimum allowed length.
  - max: The maximum allowed length.

• not(value)
  Performs a logical NOT operation on a boolean value.
  - value: The boolean value to negate.

• numeric(value, min?, max?)
  Checks numeric range constraints.
  - min: The minimum allowed value.
  - max: The maximum allowed value.

• openUrl(url)
  Opens the specified URL in a browser or handler. This function has no return value.
  - url: The URL to open.

• or(values)
  Performs a logical OR operation on a list of boolean values.
  - values: The list of boolean values to evaluate.

• pluralize(value, zero?, one?, two?, few?, many?, other)
  Returns a localized string based on the Common Locale Data Repository (CLDR) plural category of the count (zero, one, two, few, many, other). Requires an 'other' fallback. For English, just use 'one' and 'other'.
  - value: The numeric value used to determine the plural category.
  - zero: String for the 'zero' category (e.g., 0 items).
  - one: String for the 'one' category (e.g., 1 item).
  - two: String for the 'two' category (used in Arabic, Welsh, etc.).
  - few: String for the 'few' category (e.g., small groups in Slavic languages).
  - many: String for the 'many' category (e.g., large groups in various languages).
  - other: The default/fallback string (used for general plural cases).

• regex(value, pattern)
  Checks that the value matches a regular expression string.
  - pattern: The regex pattern to match against.

• required(value)
  Checks that the value is not null, undefined, or empty.
  - value: The value to check.

## Examples

```
<a2ui>
root = Column([repField, valueField])
repField = TextField("Representative", @/form/rep, "Enter name")
valueField = TextField("Deal Value", @/form/value, "0.00", "number", [?required])
@/form/rep = "John Doe"
@/form/value = 1500.00
</a2ui>
```
