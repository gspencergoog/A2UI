# A2UI Angular Renderer

The `@a2ui/angular` package provides a native Angular implementation for rendering interfaces described by the [A2UI Protocol](https://github.com/google/A2UI).

## Getting Started

### Installation

```bash
npm install @a2ui/angular @a2ui/web_core
```

### Protocol Versioning

A2UI supports multiple protocol versions. To use a specific version, use the versioned import path:

```typescript
// Use the v0.9 implementation
import { A2uiRendererService, A2UI_RENDERER_CONFIG } from '@a2ui/angular/v0_9';
import { minimalCatalog } from '@a2ui/angular/v0_9';
```

## Basic Setup (v0.9)

Configure the renderer in your `app.config.ts` using the `A2UI_RENDERER_CONFIG` injection token:

```typescript
import { ApplicationConfig } from '@angular/core';
import { A2UI_RENDERER_CONFIG, A2uiRendererService, minimalCatalog } from '@a2ui/angular/v0_9';

export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: A2UI_RENDERER_CONFIG,
      useValue: {
        catalogs: [minimalCatalog],
        actionHandler: (action) => {
          console.log('Action received:', action);
        }
      }
    },
    A2uiRendererService
  ]
};
```

## Usage

### 1. Message Processing

Inject the `A2uiRendererService` to process incoming A2UI messages from your transport layer (e.g., SSE, WebSocket).

```typescript
export class MyComponent {
  private a2ui = inject(A2uiRendererService);

  onMessageReceived(rawMessage: string) {
    const msg = JSON.parse(rawMessage);
    this.a2ui.processMessages([msg]);
  }
}
```

### 2. Rendering Surfaces

Use the `a2ui-v09-component-host` component to render individual A2UI components within your application:

```html
<a2ui-v09-component-host 
  [surfaceId]="'my-surface'" 
  [componentId]="'root'">
</a2ui-v09-component-host>
```

Alternatively, use the `a2ui-v09-surface` component to render an entire surface:

```html
<a2ui-v09-surface [surfaceId]="'my-surface'"></a2ui-v09-surface>
```

## Core Concepts

- **A2uiRendererService**: The central service that manages the connection to the A2UI Message Processor and tracks surface state.
- **ComponentHostComponent**: A wrapper component that dynamically renders A2UI components based on the current surface model.
- **SurfaceComponent**: A convenience component that renders the 'root' component of a surface.
- **Catalogs**: Collections of Angular components mapped to A2UI component types.

## Support Matrix

| Protocol Version | Status | Implementation Pattern |
|-----------------|--------|-----------------------|
| **v0.8** | Stable | Directive-based, older architecture |
| **v0.9** | Stable | Modern Angular (Signals, DI, `computed`) |

## Security Best Practices

> [!IMPORTANT]
> The sample code provided is for demonstration purposes and illustrates the mechanics of A2UI and the Agent-to-Agent (A2A) protocol. When building production applications, it is critical to treat any agent operating outside of your direct control as a potentially untrusted entity.

### Untrusted Input
Any A2UI payload received from an external agent must be treated as **untrusted input**. Malicious agents could attempt to:
- **Prompt Injection**: Provide crafted data (e.g., skill descriptions) that could manipulate your own LLM prompts.
- **Phishing**: Spoof legitimate interfaces to deceive users.
- **XSS**: Inject malicious scripts via property values if the renderer does not sanitize them.
- **DoS**: Generate excessive layout complexity to degrade client performance.

### Developer Responsibility
Developers are responsible for:
- Implementing **Content Security Policies (CSP)**.
- Strictly **sandboxing** any optional embedded content.
- **Sanitizing** inputs before using them in LLM prompts.
- Ensuring secure **credential handling**.

Failure to properly validate data and strictly sandbox rendered content can introduce severe vulnerabilities.

## License

Apache 2.0

