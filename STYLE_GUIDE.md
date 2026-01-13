# Coding Style

This project follows Google's Open Source coding standards to ensure consistency and maintainability across the codebase. We expect all contributions—whether from humans or AI assistants—to adhere to these guidelines.

## General Philosophy

*   **Consistency**: The most important rule is to be consistent with the existing code. If you are editing a file, follow the style of that file.
*   **Readability**: Code should be optimized for reading, not writing. Clear variable names and comments are essential.
*   **Automation**: Whenever possible, use automated tools (linters, formatters) to enforce style.

## Python

We follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

### Formatting & Linting

Use **Pyink** to autoformat your Python code to match Google's style.

Pyink is an open-source Python code formatter forked from Black.

### **Install Pyink**

Here is the recommended way to install `pyink`:

**Using `pipx` (Recommended for CLI tools):** `pipx` installs Python command-line applications in isolated environments, making them available system-wide without interfering with other Python projects or your system Python.

On macOS, you can install `pipx` using Homebrew:

```shell
brew install pipx
```

Here are the steps to install `pyink` using `pipx`:

```shell
# 1. Add pipx to your PATH
pipx ensurepath

# 2. Install pyink using pipx
pipx install pyink

# 3. Verify installation
pyink --version
```

Now you can run `pyink` commands directly in your shell within your GitHub checkout.

### **Configure Pyink to Match A2UI Style**

To make Pyink format code according to A2UI standards, you need to configure it. Create or modify the `pyproject.toml` file in the root of your project with the following settings:

```
[tool.pyink]
line-length = 80
unstable = true
target-version = []
pyink-indentation = 2
pyink-use-majority-quotes = true
pyink-annotation-pragmas = [
  "noqa",
  "pylint:",
  "type: ignore",
  "pytype:",
  "mypy:",
  "pyright:",
  "pyre-",
]
```

> *Note: `unstable = true` is used for newer Pyink versions (v24.3.0+). Older versions might use `preview = true`, but to match the current Google style, using an up-to-date Pyink version is best.*


### **Run Pyink:**

Navigate to your GitHub repository's directory and run Pyink.

To format specific files:

```shell
pyink my_module.py another_file.py
```

To format all Python files in the current directory and subdirectories:

```shell
pyink .
```

This setup will autoformat your Python code in the GitHub checkout to align with the Google Python Style Guide ([go/pystyle](https://goto.google.com/pystyle)).

### Key Naming Conventions

* **Functions, Variables, Methods**: `snake_case` (e.g., `calculate_total`, `user_name`)
* **Classes, Exceptions**: `PascalCase` (e.g., `HTTPRequest`, `DatabaseConnection`)
* **Constants**: `UPPER_CASE_WITH_UNDERSCORES` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
* **Private Members**: Start with a single underscore (e.g., `_internal_helper`)

### Type Hinting

* Use [Python type hints](https://docs.python.org/3/library/typing.html) for function arguments and return values.
* This helps with static analysis and IDE autocompletion.

```python
def greet(name: str) -> str:
    return f"Hello, {name}"
```

## TypeScript

We follow the [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html).

### Formatting & Linting

We use [gts](https://github.com/google/gts) (Google TypeScript Style), which provides a shared configuration for `eslint` and `prettier`.

To use `gts` in a new Typescript directory:
```bash
npx gts init
```

### Key Naming Conventions

*   **Variables, Functions, Methods**: `camelCase` (e.g., `fetchData`, `isValid`)
*   **Classes, Interfaces, Types**: `PascalCase` (e.g., `UserProfile`, `NetworkResponse`)
*   **Constants**: `UPPER_CASE` is often used for global constants, but `camelCase` is also acceptable for immutable local variables. Follow local consistency.
*   **Interfaces**: Do *not* use an `I` prefix (e.g., use `User` not `IUser`).

### Code Organization

*   **Files**: One component/class per file is preferred.
*   **Exports**: Use named exports over default exports to ensure consistent naming on import.

## Other Languages

*   **JSON**: Use 2 spaces for indentation.
*   **Markdown**: We use implementation-agnostic Markdown. Standard CommonMark or GFM is preferred.

## License Headers

All source files must include the standard Apache 2.0 license header.

```text
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
