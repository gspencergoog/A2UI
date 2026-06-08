# A2UI Protocol Evolution Guide: v0.9 to v1.0

This document serves as a comprehensive guide to the changes between A2UI version 0.9 (including 0.9.1) and version 1.0. It details the shifts in philosophy, architecture, and implementation, providing a reference for stakeholders and developers migrating between versions.

## 1. Executive summary

Version 1.0 differs from 0.9 in the following ways:

- A new client-to-server RPC mechanism allows synchronous responses to client actions (`actionResponse`) using a unique `actionId`.
- Server-to-client RPC function calls are supported via the `callFunction` message. Clients return execution results via the `functionResponse` message. Runtime execution boundaries and return types are defined in catalogs and verified at runtime, rather than being validated on the wire.
- The `theme` property in the catalog and surface creation message is replaced by `surfaceProperties`, and `primaryColor` is removed to separate layout from branding.
- Components and initial data model states can be defined directly within the `createSurface` parameters. This allows for the creation of entire UIs in a single message, rather than a create followed by separate updates.
- The `functions` field in a Catalog is now defined as a map of function name to its definition, instead of a list.
- Standard JSON Schema metadata fields (`$schema`, `$id`, `title`, and `description`) are supported in catalogs, preventing validation failures on inline catalogs with strict property checks.
- Identifier naming rules across all catalog entities (component names, function names, and argument keys) must conform to Unicode Standard Annex #31 (UAX #31).
- The `@index` built-in function dynamically retrieves iteration indices during list template rendering. The `@` prefix is reserved for core system context evaluations.

## 2. Changes

### 2.1. Catalog definition schema

- Renamed the `$defs/theme` schema to `$defs/surfaceProperties` in the Catalog schema, and removed the `primaryColor` property.
- Changed the `functions` property in the Catalog schema from a list to a map object, keyed by function name.
- Added `callableFrom` (enum: `clientOnly`, `remoteOnly`, `clientOrRemote`) to `FunctionDefinition` to restrict where a function can be invoked.
- Added an optional `instructions` field to the `Catalog` schema to embed design guidelines and component usage rules directly in the catalog, replacing the external `rules.txt` file.
- Supported standard JSON Schema metadata fields (`$schema`, `$id`, `title`, and `description`) in the Catalog object definition. Since the Catalog schema restricts properties with `additionalProperties: false`, this ensures inline catalogs containing standard schema metadata do not fail schema validation.
- Enforced Unicode Standard Annex #31 (UAX #31) identifier naming constraints (`XID_Start`, `XID_Continue`) across component names, function names, and argument keys.

### 2.2. Standard catalogs (basic and minimal)

- Added `posterUrl` property to the `Video` component in `catalogs/basic/catalog.json`, allowing a preview image to be displayed before the video plays.
- Added `placeholder` prop to the `TextField` component schema.
- Added a `steps` property to the `Slider` component schema to snap values to discrete intervals.
- Added an optional `instructions` field to the `Catalog` schema (`catalogs/basic/catalog.json`) to refer to an external guidelines/rules file (`instructions.md`) via relative file URI, renaming and updating the previous `rules.txt` file.
- Renamed `svgPath` to `path` in the custom SVG icon definition object schema.
- Renamed `$defs/theme` to `$defs/surfaceProperties` in both the basic and minimal catalogs.

### 2.3. Server-to-client messages

- Added `actionResponse` message structure (`ActionResponseMessage`) to allow the server to respond to a specific action call using a unique `actionId` with a `value` or `error`.
- Added `callFunction` message structure (`CallFunctionMessage`) to support server-initiated function execution. Removed `callableFrom` and `returnType` properties from the wire payload, relying on runtime catalog verification.
- Updated the `createSurface` message (`CreateSurfaceMessage`) to rename the `theme` field to `surfaceProperties`, and allowed passing initial `components` and `dataModel` directly inside the payload.

### 2.4. Client-to-server events

- Added `actionId` to the `action` message properties, which the client generates if a response is expected (`wantResponse: true`).
- Added `functionResponse` message structure (`FunctionResponseMessage`) to return the execution result (`value` or `error`) of a server-initiated function call.
- Updated client `error` messages to support `functionCallId` when reporting function execution failures, enforcing mutual exclusivity with `surfaceId`.

### 2.5. Client capabilities schema

- Added an optional `instructions` field to the `Catalog` object definition (`client_capabilities.json`) as a relative file URI reference (with format hint of `uri-reference`) to support external rules files associated with a catalog.
- Renamed `theme` capability block to `surfaceProperties` within the Catalog definition in `client_capabilities.json`.
- Added static `callableFrom` and `returnType` metadata properties to `FunctionDefinition` inside `client_capabilities.json` to advertise execution boundaries and return types to the server.

### 2.6. Data encoding

- Standardized data deletion behavior in `updateDataModel`. Setting a path's value to `null` deletes the key at that path. Removing or omitting keys in `updateDataModel` is no longer used for deletion.
- Removed `callableFrom` and `returnType` properties and validation constraints from `FunctionCall` and dynamic value schemas in `common_types.json`, deferring boundary checking and return type validation entirely to runtime execution.
- Added built-in `@index` function (with optional `offset` parameter) under `FunctionCall` to retrieve the iteration index during list template rendering. Reserved the `@` prefix for core system context evaluations.

### 2.7. Processing rules

- Explicitly specified that `surfaceId` must be globally unique per client session. Creating a surface with an ID that already exists (without first deleting it) is an error.
- Enforced runtime lookup of function execution boundaries and return types. If a client receives a remote call to a function configured as `clientOnly` or if the function is unregistered, it rejects the call and returns an error with the code `INVALID_FUNCTION_CALL`.
- Enforced catalog entity naming compliance with Unicode Standard Annex #31 (UAX #31).
- Restricted `@index` evaluation scope strictly to template instantiation loops (Collection Scope). Calling `@index` outside of template iteration results in an evaluation error.

## 3. Migration guide

This section outlines the steps required to migrate existing applications and components from version 0.9 (including 0.9.1) to version 1.0.

### For agents and servers

- If doing inference directly based on JSON schema, update the pointers to load v1.0 schemas instead of v0.9.
- If returning pre-generated content, or using examples, update the examples to conform to the 1.0 schemas, and set up validation tests to verify this.
- If using an alternative inference format (e.g. DSL), update it to convert the 1.0 catalog format to the DSL prompt, and convert the DSL output to A2UI 1.0 format.
- Ensure all generated catalog entity names conform to UAX #31 identifier rules.
- Do not include `callableFrom` or `returnType` properties in wire-level `FunctionCall` payloads.

### For renderers and clients

- Implement function execution by adding support for parsing `callFunction` messages, checking boundary definitions in the catalog (`callableFrom`), rejecting invalid calls with `INVALID_FUNCTION_CALL`, and returning `functionResponse` messages.
- Support synchronous action responses by generating `actionId` for actions with `wantResponse: true` and writing returned values from `actionResponse` messages into the data model.
- Support simultaneous version handling during session initialization by inspecting the `version` property to route payloads to version-specific controllers.
- Enforce surface uniqueness by raising an error if `createSurface` is received for an existing `surfaceId`.
- Update error reporting to handle `functionCallId` and enforce mutual exclusivity with `surfaceId`.
- Enforce Unicode identifier naming by verifying that all catalog entity names (components, functions, prop keys) conform to UAX #31 identifier rules.
- Support built-in `@index` evaluation during list template rendering (Collection Scope) to provide the 0-based iteration index, adjusted by any `offset` parameter.
