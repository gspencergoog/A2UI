# A2UI Express Evolutionary Mutation Prompt

You are an expert compiler optimization agent. Your goal is to mutate the reigning A2UI Express DSL technical specification, prompt generator, parser, and decompiler in lockstep to increase token compression efficiency and prompt compactness without losing semantic expressive power.

## Optimization objectives

1. **Radical DSL Redesign:** You are fully empowered to redesign the DSL format entirely (e.g., Lisp s-expressions `(Column (TextField ...))`, YAML/Indentation-based structural hierarchies, Assembler-style opcode stacks, or custom shorthand overloads) to minimize token footprint.
2. **Dynamic Feature Masking:** When updating `prompt_generator.py`, introduce dynamic pruning to filter catalog signatures based on active scenario requirements and eliminate static boilerplate.
3. **Autonomous Structural Elision:** Modify `compiler.py` and `decompiler.py` autonomously to support advanced shorthands (such as optional trailing nulls, omitted brackets, and property packing).
4. **Lockstep Synchrony:** You must modify all four core files simultaneously so that the mutated compiler correctly tokenizes and parses the mutated grammar, and the decompiler translates standard JSON back into the new syntax.
5. **AST Robustness:** The updated Python parser (`compiler.py`), decompiler (`decompiler.py`), and prompt generator (`prompt_generator.py`) must be syntactically valid Python code and parse cleanly into an Abstract Syntax Tree.
6. **Compile-Time Adherence:** Update both the compiler and decompiler to support your proposed DSL paradigm, ensuring it successfully parses your translated golden reference sample:

<TIER0_GOLDEN_TARGET>
root = Column([repField, valueField])
repField = TextField("Representative", @/form/rep, "Enter name")
valueField = TextField("Deal Value", @/form/value, "0.00", "number", ?required)
</TIER0_GOLDEN_TARGET>
7. **Mandatory Documentation Preservation:** When updating `prompt_generator.py`, you MUST ensure that all generated system prompts preserve ALL descriptions for components, component properties, functions, and function arguments exactly as written. DO NOT delete, shorten, or summarize any descriptive text or parameter usage explanations.

## Current reigning champion baseline

<REIGNING_CHAMPION>
### a2ui_express.md
{A2UI_EXPRESS_CONTENT}

### prompt_generator.py
{PROMPT_GENERATOR_CONTENT}

### compiler.py
{COMPILER_CONTENT}

### decompiler.py
{DECOMPILER_CONTENT}
</REIGNING_CHAMPION>

## Output contract

You must respond with precisely four XML blocks containing the fully updated, drop-in replacement file contents. Do not include introductory filler, markdown backticks outside the XML blocks, or high-level summaries.

<OUTPUT_CONTRACT>
<a2ui_express.md>
...fully updated markdown specification...
</a2ui_express.md>

<prompt_generator.py>
...fully updated Python prompt generator class...
</prompt_generator.py>

<compiler.py>
...fully updated Python compiler logic...
</compiler.py>

<decompiler.py>
...fully updated Python decompiler logic...
</decompiler.py>
</OUTPUT_CONTRACT>
