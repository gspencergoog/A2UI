# A2UI Renderers Architecture

## 1. Introduction and Goals

This document outlines the target architecture for A2UI client-side renderers, specifically focusing on the Angular renderer and its relationship with the cross-framework `@a2ui/web_core` library.

**Goals:**

1. **Strict Protocol Version Separation:** Completely separate the implementations of A2UI v0.8 and v0.9 within the renderers. Prevent any runtime conversion or polyfilling (e.g., converting a v0.9 message to a v0.8 structure for processing).
2. **Cross-Framework Foundation (`web_core`):** Ensure that `@a2ui/web_core` provides all necessary data structures, message processing, and evaluation tools so that _any_ web-based renderer (Angular, React, Vue, Vanilla JS) can build upon it.
3. **Extraction of Standard Logic:** Move the implementation of the expression parser, evaluator, and the "basic catalog" functions out of the Angular renderer and into `web_core` (or a dedicated sibling package/module), without making the basic catalog strictly required for all consumers.
4. **Configuration-Driven Versioning:** Renderers should be able to switch between protocol versions (e.g., v0.8 vs v0.9) purely via configuration during initialization, rather than via complex branch logic during rendering.
5. **Multi-Version Handshake Resolution:** To be robust, renderers must dynamically agree upon a supported protocol version with the server at runtime (the initial handshake negotiation) and then freeze this logical execution pipeline for the remainder of the session.

---

## 2. Current State and Challenges

Currently, the `renderers/angular` package contains a mix of responsibilities:

- It "sort of" implements v0.9, but frequently bridges the gap by adapting/converting constructs back to v0.8 formats.
- The `ExpressionParser`, `ExpressionEvaluator`, and implementations of basic standard functions (like `formatString`, arithmetic, etc.) are tightly coupled to Angular (`@Injectable`, InjectionTokens).
- The Angular renderer's `MessageProcessor` subclass tries to hack around the v0.9 `web_core` generic types, passing a dummy catalog shape just to satisfy instantiation bounds.

This creates technical debt and prevents other frameworks from easily implementing an A2UI renderer without rewriting the complex string interpolation and function resolution logic.

---

## 3. Target Architecture

The target architecture enforces a strict layered approach alongside dynamic capability injection based on environment initialization:

### 3.1. Layer 1: Protocol Processing (`web_core/{v0_8, v0_9}`)

The `web_core` package will maintain strictly separated modules for each protocol version.

- `@a2ui/web_core/v0_8/processing`
- `@a2ui/web_core/v0_9/processing`

Each version module will expose its own `MessageProcessor`, `DataModel`, `SurfaceModel`, and interfaces. These models are purely logical and have zero knowledge of any UI framework.

Crucially, **each module does not know the other exists.**

### 3.2. Layer 2: Basic Catalog and Expression Logic (`web_core/basic_catalog`)

The implementation of standard functions and string interpolation (the Expression Evaluator) is _not_ inherently tied to v0.9 core processing, nor is it unique to Angular. It is specific to the basic catalog, and doesn't apply to other catalogs.

**Extraction:**

- Move `ExpressionParser` and `ExpressionEvaluator` from `renderers/angular/src/lib/` to `renderers/web_core/src/basic_catalog/expressions/`.
- Move `BASIC_FUNCTIONS` (e.g., `add`, `formatString`, `formatDate`) to `renderers/web_core/src/basic_catalog/functions/`.

**Agnosticism:**
These utilities will be written in pure TypeScript. They will take a generic `EvaluationContext` (capable of resolving paths and providing the parser) and will not depend on Angular's Dependency Injection.

### 3.3. Layer 3: Framework Renderers (e.g., `renderers/angular`)

The framework renders are reduced to essentially structural wiring.

1. **Protocol Handshake & Pipeline Locking:**
   The application initiates its session with the server and receives the target schema payload. The Renderer examines this handshake and statically routes its internal processing engine pointing toward exactly ONE of the resolved architectures. Once the session selects v0.8 or v0.9, the pipeline is locked; no individual message switching happens during session execution.

2. **Isolating Main UI Elements:**
   This implies the visual templates (the things rendering standard structures like `Row` or `Text` components) observe a normalized view interface _or_ multiple catalog configurations are mapped accordingly avoiding overlapping code pollution.

**Dynamic Version Initialization Example:**

```typescript
import { provideA2UI } from "@a2ui/angular";
import { A2uiSessionConnection } from "@a2ui/web_core"; // Connection API
import { V09Processor, V09Catalog } from "@a2ui/web_core/v0_9";
import { V08Processor, V08Catalog } from "@a2ui/web_core/v0_8";
import {
  ExpressionEvaluator,
  BasicFunctions,
} from "@a2ui/web_core/basic_catalog";

// Framework entry logic:
export const initializeAppWithRenderer = async () => {
  // 1. Establish initial Handshake
  const session = await A2uiSessionConnection.connect("/a2ui-endpoint");

  // 2. Negotiate Supported Capabilities Structure
  const resolvedVersion = session.negotiatedVersion; // '0.9'

  // 3. Construct specific configuration block mapping processing & UI Catalog
  let a2uiConfiguration;

  if (resolvedVersion === "0.9") {
    a2uiConfiguration = {
      processor: new V09Processor(),
      catalog: V09Catalog,
      evaluator: new ExpressionEvaluator(BasicFunctions),
    };
  } else if (resolvedVersion === "0.8") {
    a2uiConfiguration = {
      processor: new V08Processor(),
      catalog: V08Catalog, // Separate implementation logic
      evaluator: new ExpressionEvaluator(BasicFunctions),
    };
  }

  // 4. Mount application UI passing fixed context
  bootstrapApplication(AppComponent, {
    providers: [provideA2UI(a2uiConfiguration)],
  });
};
```

---

## 4. Implementation Steps

1.  **Extract Expression Logic:** Relocate `expression_parser.ts`, `expression_evaluator.ts`, and `catalog/basic_functions.ts` from `renderers/angular` to a new directory `renderers/web_core/src/basic_catalog`. Remove Angular-specific `@Injectable` and injection tokens from these files.
2.  **Clean up `web_core` API Surfaces:** Ensure that `@a2ui/web_core/v0_8` and `@a2ui/web_core/v0_9` correctly export their completely isolated sets of processing and state classes.
3.  **Implement Handshake Discovery:** Construct an initial configuration router in the primary consumer endpoint that defers Angular initialization until the `a2ui` handshake completes, selecting the targeted Processor protocol.
4.  **Remove Version Adapters:** Strip out any code in the Angular renderer that checks for v0.9 message shapes and transforms them into v0.8 shapes before passing them down. The underlying `web_core/v0_9/processing/message-processor.ts` must handle the v0.9 messages natively, and the Angular UI must bind directly to the v0.9 `SurfaceModel`.
5.  **Angular Standard Catalog Separation Updates:** The Angular catalogs components (e.g. `AngularText`) must map accurately against the agreed target processor models (meaning one catalog instance exclusively references one specification implementation, rather than using logical branching over component types dynamically).
