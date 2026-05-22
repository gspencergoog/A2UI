# A2UI Express Output Contract

You must output the user interface using the compact A2UI Express DSL notation.

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

5. Data bindings: prefix absolute paths in the data model with '$', e.g., $/user/firstName.
   Prefix relative list scopes with '$', e.g., $firstName.

6. Logic and validation: prefix client check rules with '?', e.g., ?required or
   ?regex("^[0-9]5$").

7. Action events: represent server-side actions using the Event helper:
   Event("save_deal", {rep: $/form/rep})

8. Nested functions: call client functions directly using catalog signatures,
   for example openUrl("https://example.com").

## Positional Component Signatures

Use these exact positional signatures to instantiate components. Do not output property keys:
• AudioPlayer(url, description?)
• Button(child, variant?, action, checks?)
• Card(child)
• CheckBox(label, value, checks?)
• ChoicePicker(label?, variant?, options, value, displayStyle?, filterable?, checks?)
• Column(children, justify?, align?)
• DateTimeInput(value, enableDate?, enableTime?, min?, max?, label?, checks?)
• Divider(axis?)
• Icon(name)
• Image(url, description?, fit?, variant?)
• List(children, direction?, align?)
• Modal(trigger, content)
• Row(children, justify?, align?)
• Slider(label?, min?, max, value, checks?)
• Tabs(tabs)
• Text(text, variant?)
• TextField(label, value?, placeholder?, variant?, checks?)
• Video(url, posterUrl?)

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
root = Column([repField, valueField])
repField = TextField("Representative", $/form/rep, "Enter name")
valueField = TextField("Deal Value", $/form/value, "0.00", "number", [?required])
```

