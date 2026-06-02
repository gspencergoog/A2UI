# Evaluation of new features in v0.10

This document evaluates the new protocol features introduced in A2UI version 0.10. It provides an objective critique of their specifications, identifies potential technical edge cases, and presents recommendations to improve the clarity and security of the protocol before ratification.

The new features added in v0.10 focus on extending the unidirectional streaming model of v0.9 into a bidirectional, state-synchronized exchange. This is achieved through client action responses and server-initiated function execution. Additionally, minor usability properties are added to the basic component catalog.

---

## Bidirectional client action response

### Protocol description

Version 0.10 allows a client to trigger an `action` with `wantResponse` set to `true` and a unique `actionId`. The server then responds with an `actionResponse` message. Additionally, the client-side `Action` definition includes a `responsePath` parameter which specifies a JSON Pointer where the returned value should be stored in the local data model.

### Criticisms and edge cases

- **Response timeouts and memory leaks**: The specification does not define a lifecycle or timeout for pending action responses. If a server fails to respond or shuts down, the client might keep the response listener active in memory indefinitely.
- **Concurrent action handling**: The protocol does not specify whether a component should block further user input while an action is pending. For example, if a user clicks a submit button twice before the first response arrives, the client will send two distinct action requests with different IDs. This can lead to race conditions in state updates.
- **Data model type safety**: When the server returns a value to be written to `responsePath`, there is no verification that the returned value matches the schema or data type expected by the components bound to that path. A mismatched type (e.g., returning an integer when a string is expected) can cause rendering errors.

### Recommendations for improvement

- Define a standard client timeout (such as 15 seconds). If no response is received within this period, the client must automatically unregister the listener, free associated memory, and trigger a local `VALIDATION_FAILED` or network error event.
- Specify that interactive components must disable themselves or transition to a loading state once an action with `wantResponse: true` is triggered.
- Mandate that the client must validate the returned value structure against any schemas bound to `responsePath` before writing it to the local data model.

---

## Server initiated function calls

### Protocol description

The server can send a `callFunction` message containing a `functionCallId` and `wantResponse` flag to execute a registered function on the client. The client runs the function and sends the output back via a `functionResponse` message or an `error` message. The `callableFrom` enum (`clientOnly`, `remoteOnly`, `clientOrRemote`) restricts where a function can be executed.

### Criticisms and edge cases

- **Execution boundary violations**: A server might attempt to invoke a function defined in the catalog as `clientOnly`. While the schema lists this restriction, the protocol does not explicitly define the client's rejection behavior.
- **Redundancy of the `callableFrom` wire field**: The `callFunction` message schema in `server_to_client.json` requires the server to specify `callableFrom` as `"remoteOnly"` or `"clientOrRemote"`. However, a buggy or malicious server could simply declare the field as `"remoteOnly"` in the message while attempting to invoke a `"clientOnly"` function. Since the static schema validator cannot verify the message against the active component catalog at parse time, the client must perform a runtime validation check against its local catalog registry anyway. This renders the wire-level `callableFrom` property entirely redundant and secure-by-declaration only, adding unnecessary payload weight.
- **Circular execution loops**: A server-initiated function call can write to the data model, which triggers a client-side binding, which in turn triggers another action or function call. This can lead to infinite circular execution chains that degrade client performance.
- **Security risks of arguments**: Client-side functions can perform actions like navigating, playing audio, or fetching remote files. If the server passes unvalidated arguments to these functions, it introduces security vulnerabilities.

### Recommendations for improvement

- **Omit `callableFrom` from the wire envelope**: Remove the `callableFrom` property from the `CallFunctionMessage` schema in `server_to_client.json`. Instead, boundary enforcement must be specified strictly as a client-side runtime check. The client must look up the function name in its catalog, verify that the registered function is configured as `remoteOnly` or `clientOrRemote`, and reject the call immediately with an error code `INVALID_FUNCTION_CALL` if it is configured as `clientOnly` or is missing.
- Mandate that all arguments supplied in a `callFunction` message must be strictly validated against the function's schema definition on the client before execution.
- Suggest capping the maximum nesting depth of reactive updates to prevent infinite loop propagation.

---

## Basic catalog component properties

### Protocol description

Three properties are added to standard components:

- `steps` (integer, minimum 1) for `Slider` to define discrete track divisions.
- `posterUrl` (string) for `Video` to display a preview image.
- `placeholder` (string) for `TextField` to display helper hints.

### Criticisms and recommendations

- **Slider step calculations**: The specification does not define how to resolve fractional values when the value range is divided by `steps`. For example, if the slider has a range from 0.0 to 1.0 with 3 steps, the snapping positions are 0.0, 0.333..., 0.666..., and 1.0. The spec should clarify that values are rounded to the nearest snap interval calculated as `min + round((value - min) / interval) * interval`, where `interval = (max - min) / steps`.
- **Placeholder default**: Specify that the `placeholder` property must default to an empty string if it is omitted or set to null.

---

## Summary of recommended improvements

- Introduce a standard 15-second client-side timeout for all pending action responses and function execution payloads.
- Require that clients validate the returned payload format against expected local schemas prior to writing values to the local data model.
- Omit the redundant `callableFrom` property from the `callFunction` message payload in `server_to_client.json`, enforcing execution boundaries strictly at runtime on the client.
- Define standard interval calculations for fractional slider steps and standard fallback defaults for input placeholders.
