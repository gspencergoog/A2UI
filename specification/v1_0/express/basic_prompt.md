# A2UI Express Output Contract
Output UI in A2UI Express DSL within <a2ui>...</a2ui>.

[CRITICAL]
- ALWAYS name the target variable 'root' (e.g. root = Component(...)). NEVER use other names.
- NO markdown code fences. Output only raw DSL.

## Rules
1. var=Component(args)
2. str/enum,42,bool,null
3. Arrays:[a,b]
4. Paths:@/path,@rel
5. Rules:?req,?regex(pat)
6. Event("name",{k:v})
7. Nested:openUrl(url)
8. Data:@/path=val

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
repField = TextField("Rep", @/form/rep, "Name")
@/form/rep = "John Doe"
</a2ui>
