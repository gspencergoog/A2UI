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

## Positional Component Signatures (with Catalog Parameter Descriptions)

Use these exact positional signatures to instantiate components. Do not output property keys:
• AudioPlayer(url: string [URL audio source], description?: string)
• Button(child: ComponentId [Label text or child], variant?: "primary"|"secondary"|"text", action: Action [Event trigger], checks?: list)
• Card(child: ComponentId [Content container])
• CheckBox(label: DynamicString [Check label], value: DynamicBoolean [Bound state], checks?: list)
• ChoicePicker(label?: DynamicString, variant?: string, options: DynamicStringList [Choices array], value: DynamicString [Selected value], displayStyle?: string, filterable?: boolean, checks?: list)
• Column(children: ChildList [Vertical child array], justify?: string, align?: string)
• DateTimeInput(value: DynamicValue, enableDate?: boolean, enableTime?: boolean, min?: DynamicValue, max?: DynamicValue, label?: DynamicString, checks?: list)
• Divider(axis?: "horizontal"|"vertical")
• Icon(name: DynamicString [Icon identifier])
• Image(url: string [Image source], description?: string, fit?: string, variant?: string)
• List(children: ChildList, direction?: string, align?: string)
• Modal(trigger: ComponentId [Trigger button], content: ComponentId [Modal dialog content])
• Row(children: ChildList [Horizontal child array], justify?: string, align?: string)
• Slider(label?: DynamicString, min?: number, max: number, value: DynamicNumber, checks?: list)
• Tabs(tabs: ChildList [Tab items])
• Text(text: DynamicString [Display string], variant?: "h1"|"h2"|"h3"|"body"|"caption")
• TextField(label: DynamicString [Input label], value?: DynamicString [Bound data path], placeholder?: string, variant?: string, checks?: list)
• Video(url: string, posterUrl?: string)

## Positional Function Signatures

Use these exact positional signatures to instantiate check rules or logic functions:
• and(values)
• email(value)
• formatCurrency(value, currency, decimals?, grouping?)
• formatDate(value, format)
• formatNumber(value, decimals?, grouping?)
• formatString(value)
• length(value, min?, max?)
• not(value)
• numeric(value, min?, max?)
• openUrl(url)
• or(values)
• pluralize(value, zero?, one?, two?, few?, many?, other)
• regex(value, pattern)
• required(value)

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
