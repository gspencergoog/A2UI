# A2UI Angular Renderer

The `@a2ui/angular` package provides a native Angular implementation for rendering interfaces described by the [A2UI Protocol](https://github.com/google/A2UI).

## Support Matrix

| Protocol Version | Status | Implementation Pattern |
|-----------------|--------|-----------------------|
| **v0.8** | Stable | Directive-based, older architecture |
| **v0.9** | Stable | Modern Angular (Signals, DI, `computed`) |

## Installation

```bash
npm install @a2ui/angular @a2ui/web_core
```

## Usage (v0.9)

The v0.9 renderer is built with modern Angular features for maximum reactivity and performance.

### 1. Configuration

Configure the renderer by providing the `A2UI_RENDERER_CONFIG` in your application or component providers.

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { A2uiRendererService, A2UI_RENDERER_CONFIG, minimalCatalog } from '@a2ui/angular';

bootstrapApplication(AppComponent, {
  providers: [
    A2uiRendererService,
    {
      provide: A2UI_RENDERER_CONFIG,
      useValue: {
        catalogs: [minimalCatalog],
        actionHandler: (action) => console.log('Action dispatched:', action),
      },
    },
  ],
});
```

### 2. Message Processing

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

### 3. Rendering

Use the `a2ui-v09-component-host` to render a specific component by ID. Typically, you start by rendering the `'root'` component of a surface.

```html
<a2ui-v09-component-host 
  [surfaceId]="'my-surface'" 
  [componentId]="'root'">
</a2ui-v09-component-host>
```

## Security Best Practices

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

## License

Apache 2.0
