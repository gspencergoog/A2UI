# A2UI Express Output Contract

You must output the user interface using the compact A2UI Express DSL notation.
You MUST surround the entire A2UI Express DSL block with the sentinel tags `<a2ui>` and `</a2ui>`.

## Grammar Rules

1. Output exactly one variable assignment statement per line:
   variable_name = ComponentName(arg1, arg2, ...)

2. The interface tree must have a single entry point assigned to the reserved variable 'root'.

3. Primitives:
   - Strings: enclose in double quotes (e.g. "label") or write unquoted for lowercase keywords (e.g. primary)
   - Numbers: write as integers or decimals (e.g. 42)
   - Booleans: write true or false
   - Null values: write null

4. Lists: represent as arrays, e.g., [child1, child2]

5. Data bindings: prefix absolute paths in the data model with '@', e.g., @/user/firstName.
   Prefix relative list scopes with '@', e.g., @firstName.

6. Logic and validation: prefix client check rules with '?', e.g., ?required or ?regex("^[0-9]{5}$").

7. Action events: represent server-side actions using the Event helper:
   Event("save_deal", {rep: @/form/rep})

8. Nested functions: call client functions directly using catalog signatures, for example openUrl("https://example.com").

9. Data model population: Assign a value directly to an absolute data path (e.g. @/path/to/key = "value") to populate values inside dataModel.

## Positional Component Signatures

Use these exact positional signatures to instantiate components. Do not output property keys:

• AudioPlayer(url: string, description?: string)
  Renders a simple HTML5 audio player.
  - url: The URL of the audio file to play
  - description: Optional text describing the audio content

• Button(child: ComponentId, variant?: "primary"|"secondary"|"text", action: Action, checks?: list)
  A standard button component that triggers an action.
  - child: The ID of the child component (typically Text or Icon) to display inside the button
  - variant: The visual style variant: 'primary', 'secondary', or 'text'
  - action: The interaction handler executed when clicked
  - checks: Optional validation check rules

• Card(child: ComponentId)
  A surface container with subtle elevation and rounded corners.
  - child: The ID of the content component to display inside the card

• CheckBox(label: DynamicString, value: DynamicBoolean, checks?: list)
  A boolean toggle switch or traditional checkbox.
  - label: Text label displayed beside the switch
  - value: Bound JSON Pointer path to a boolean in the data model
  - checks: Optional validation check rules

• ChoicePicker(label?: DynamicString, variant?: string, options: DynamicStringList, value: DynamicString, displayStyle?: string, filterable?: boolean, checks?: list)
  A single-select dropdown or chip group.
  - label: Optional text label displayed above the picker
  - variant: Optional color variant
  - options: Array of selection option strings
  - value: Bound data path where the selected option string is saved
  - displayStyle: Optional rendering style ('dropdown', 'radio', 'chips')
  - filterable: If true, enables client-side search filtering
  - checks: Optional validation check rules

• Column(children: ChildList, justify?: string, align?: string)
  A layout component that arranges its children vertically. To create a grid layout, nest Rows within this Column.
  - children: Array of child component IDs or dynamic list template
  - justify: Vertical alignment distribution along the main axis ('start', 'center', 'end', 'space-between')
  - align: Horizontal cross-axis alignment ('start', 'center', 'end', 'stretch')

• DateTimeInput(value: DynamicValue, enableDate?: boolean, enableTime?: boolean, min?: DynamicValue, max?: DynamicValue, label?: DynamicString, checks?: list)
  A date, time, or datetime selection picker.
  - value: Bound data path for the selected timestamp
  - enableDate: If true, enables calendar date selection
  - enableTime: If true, enables clock time selection
  - min: Minimum allowed timestamp
  - max: Maximum allowed timestamp
  - label: Optional accessible label
  - checks: Optional validation check rules

• Divider(axis?: "horizontal"|"vertical")
  A visual line separating structural sections.
  - axis: Orientation axis ('horizontal', 'vertical')

• Icon(name: DynamicString)
  Renders a material design icon.
  - name: Material design icon name string (e.g., 'check', 'close')

• Image(url: string, description?: string, fit?: string, variant?: string)
  Renders an image from a URL.
  - url: The absolute URL of the image source
  - description: Accessible alt description for screen readers
  - fit: Image scaling fit ('cover', 'contain', 'fill')
  - variant: Optional visual border variant

• List(children: ChildList, direction?: string, align?: string)
  A virtualized list container.
  - children: Dynamic list template or child component array
  - direction: Scrolling direction ('vertical', 'horizontal')
  - align: Cross-axis item alignment

• Modal(trigger: ComponentId, content: ComponentId)
  A popup overlay or modal dialog.
  - trigger: The button component ID that opens the modal
  - content: The container component ID displayed inside the popup

• Row(children: ChildList, justify?: string, align?: string)
  A layout component that arranges its children horizontally.
  - children: Array of child component IDs
  - justify: Horizontal alignment distribution along the main axis ('start', 'center', 'end', 'space-between')
  - align: Vertical cross-axis alignment ('start', 'center', 'end', 'stretch')

• Slider(label?: DynamicString, min?: number, max: number, value: DynamicNumber, checks?: list)
  A numeric slider input.
  - label: Optional accessible label
  - min: Minimum allowed numeric value
  - max: Maximum allowed numeric value
  - value: Bound data path for the slider number
  - checks: Optional validation check rules

• Tabs(tabs: ChildList)
  A tabbed navigation container.
  - tabs: Array of Tab component IDs

• Text(text: DynamicString, variant?: "h1"|"h2"|"h3"|"body"|"caption")
  Renders formatted plain text or headings.
  - text: The string content to display
  - variant: Typographic scale variant ('h1', 'h2', 'h3', 'body', 'caption')

• TextField(label: DynamicString, value?: DynamicString, placeholder?: string, variant?: string, checks?: list)
  A standard text input field.
  - label: Accessible label displayed above or inside the input
  - value: Bound JSON Pointer path to the data model
  - placeholder: Hint text shown when empty
  - variant: Input mode constraint ('text', 'number', 'password', 'email')
  - checks: Optional validation check rules

• Video(url: string, posterUrl?: string)
  Renders an HTML5 video player.
  - url: The absolute URL of the video source
  - posterUrl: Optional preview poster image URL

## Positional Function Signatures

Use these exact positional signatures to instantiate check rules or logic functions:

• and(values: list)
  Performs a logical AND operation on a list of boolean values.
  - values: Array of boolean expressions or bound paths

• email(value: DynamicString)
  Checks that the value is a valid email address.
  - value: The string value to validate

• formatCurrency(value: DynamicNumber, currency: string, decimals?: number, grouping?: boolean)
  Formats a number as a currency string.
  - value: Numeric monetary amount
  - currency: ISO 4217 currency code (e.g., 'USD', 'EUR')
  - decimals: Optional number of decimal places
  - grouping: If true, uses locale grouping separators

• formatDate(value: DynamicValue, format: string)
  Formats a timestamp into a string using a pattern.
  - value: Timestamp value to format
  - format: Unicode TR35 date pattern string (e.g., 'MMM dd, yyyy')

• formatNumber(value: DynamicNumber, decimals?: number, grouping?: boolean)
  Formats a number with the specified grouping and decimal precision.
  - value: The number to format
  - decimals: Optional number of decimal places
  - grouping: If true, uses locale grouping separators

• formatString(value: DynamicString)
  Performs string interpolation of data model values and other functions.
  - value: Template string containing interpolated expressions (e.g., 'Hello ${/name}')

• length(value: DynamicString, min?: number, max?: number)
  Checks string length constraints.
  - value: The string value to check
  - min: Minimum allowed character count
  - max: Maximum allowed character count

• not(value: DynamicBoolean)
  Performs a logical NOT operation on a boolean value.
  - value: Boolean expression to negate

• numeric(value: DynamicNumber, min?: number, max?: number)
  Checks numeric range constraints.
  - value: The numeric value to verify
  - min: Minimum allowed number
  - max: Maximum allowed number

• openUrl(url: string)
  Opens the specified URL in a browser.
  - url: Absolute URL string to open

• or(values: list)
  Performs a logical OR operation on a list of boolean values.
  - values: Array of boolean expressions or bound paths

• pluralize(value: DynamicNumber, zero?: string, one?: string, two?: string, few?: string, many?: string, other: string)
  Returns a localized string based on the CLDR plural category.
  - value: Numeric count determining plural category
  - zero: String for zero items
  - one: String for singular item
  - two: String for two items
  - few: String for few items
  - many: String for many items
  - other: Fallback default plural string

• regex(value: DynamicString, pattern: string)
  Checks that the value matches a regular expression string.
  - value: The string value to validate
  - pattern: Regex pattern string to match against

• required(value: DynamicValue)
  Checks that the value is not null, undefined, or empty.
  - value: The target value to verify

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
