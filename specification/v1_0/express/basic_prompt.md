# A2UI Express Output Contract
Output UI in compact A2UI Express DSL. Surround with `<a2ui>` and `</a2ui>`.

[CRITICAL]
- ALWAYS name the target variable 'root' (e.g. `root = Component(...)`). NEVER use other names like `submitBtn = ...`.
- NO markdown code fences/backticks. Output only raw DSL.

## Rules
1. One assignment/line: var = Component(args...)
2. Single root named 'root'.
3. "str", 42, true/false, null.
4. Arrays: [a,b].
5. Bindings: $/path or $relative.
6. Rules: ?required or ?regex(pat).
7. Actions: Event("name", {rep: $/path}).
8. Nested: openUrl(url).
9. Data: $/path = val.

## Signatures
AudioPlayer(url,description?)
Button(child,variant?,action,checks?)
Card(child)
CheckBox(label,value,checks?)
ChoicePicker(label?,variant?,options,value,displayStyle?,filterable?,checks?)
Column(children,justify?,align?)
DateTimeInput(value,enableDate?,enableTime?,min?,max?,label?,checks?)
Divider(axis?)
Icon(name)
Image(url,description?,fit?,variant?)
List(children,direction?,align?)
Modal(trigger,content)
Row(children,justify?,align?)
Slider(label?,min?,max,value,checks?)
Tabs(tabs)
Text(text,variant?)
TextField(label,value?,placeholder?,variant?,checks?)
Video(url,posterUrl?)

and(values)
email(value)
formatCurrency(value,currency,decimals?,grouping?)
formatDate(value,format)
formatNumber(value,decimals?,grouping?)
formatString(value)
length(value,min?,max?)
not(value)
numeric(value,min?,max?)
openUrl(url)
or(values)
pluralize(value,zero?,one?,two?,few?,many?,other)
regex(value,pattern)
required(value)

## Example
<a2ui>
root = Column([repField])
repField = TextField("Rep", $/form/rep, "Name")
$/form/rep = "John Doe"
</a2ui>
