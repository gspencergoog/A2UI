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

## Positional Component Signatures (with Descriptions)

Use these exact positional signatures to instantiate components. Do not output property keys:

• AudioPlayer(url: string [URL audio source], description?: string)
  Renders a simple HTML5 audio player.

• Button(child: ComponentId [Label text or child], variant?: "primary"|"secondary"|"text", action: Action [Event trigger], checks?: list)
  A standard button component that triggers an action.

• Card(child: ComponentId [Content container])
  A surface container with subtle elevation and rounded corners.

• CheckBox(label: DynamicString [Check label], value: DynamicBoolean [Bound state], checks?: list)
  A boolean toggle switch or traditional checkbox.

• ChoicePicker(label?: DynamicString, variant?: string, options: DynamicStringList [Choices array], value: DynamicString [Selected value], displayStyle?: string, filterable?: boolean, checks?: list)
  A single-select dropdown or chip group.

• Column(children: ChildList [Vertical child array], justify?: string, align?: string)
  A layout component that arranges its children vertically. To create a grid layout, nest Rows within this Column.

• DateTimeInput(value: DynamicValue, enableDate?: boolean, enableTime?: boolean, min?: DynamicValue, max?: DynamicValue, label?: DynamicString, checks?: list)
  A date, time, or datetime selection picker.

• Divider(axis?: "horizontal"|"vertical")
  A visual line separating structural sections.

• Icon(name: DynamicString [Icon identifier])
  Renders a material design icon.

• Image(url: string [Image source], description?: string, fit?: string, variant?: string)
  Renders an image from a URL.

• List(children: ChildList, direction?: string, align?: string)
  A virtualized list container.

• Modal(trigger: ComponentId [Trigger button], content: ComponentId [Modal dialog content])
  A popup overlay or modal dialog.

• Row(children: ChildList [Horizontal child array], justify?: string, align?: string)
  A layout component that arranges its children horizontally.

• Slider(label?: DynamicString, min?: number, max: number, value: DynamicNumber, checks?: list)
  A numeric slider input.

• Tabs(tabs: ChildList [Tab items])
  A tabbed navigation container.

• Text(text: DynamicString [Display string], variant?: "h1"|"h2"|"h3"|"body"|"caption")
  Renders formatted plain text or headings.

• TextField(label: DynamicString [Input label], value?: DynamicString [Bound data path], placeholder?: string, variant?: string, checks?: list)
  A standard text input field.

• Video(url: string, posterUrl?: string)
  Renders an HTML5 video player.

## Positional Function Signatures (with Descriptions)

Use these exact positional signatures to instantiate check rules or logic functions:

• and(values)
  Performs a logical AND operation on a list of boolean values.

• email(value)
  Checks that the value is a valid email address.

• formatCurrency(value, currency, decimals?, grouping?)
  Formats a number as a currency string.

• formatDate(value, format)
  Formats a timestamp into a string using a pattern.

• formatNumber(value, decimals?, grouping?)
  Formats a number with the specified grouping and decimal precision.

• formatString(value)
  Performs string interpolation of data model values and other functions.

• length(value, min?, max?)
  Checks string length constraints.

• not(value)
  Performs a logical NOT operation on a boolean value.

• numeric(value, min?, max?)
  Checks numeric range constraints.

• openUrl(url)
  Opens the specified URL in a browser.

• or(values)
  Performs a logical OR operation on a list of boolean values.

• pluralize(value, zero?, one?, two?, few?, many?, other)
  Returns a localized string based on the CLDR plural category.

• regex(value, pattern)
  Checks that the value matches a regular expression string.

• required(value)
  Checks that the value is not null, undefined, or empty.

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
