### Proposal: Improving Angular Component APIs via web_core Integration

Based on an analysis of the current Angular codebase and the React renderer prototype, I propose the following architectural improvements to streamline component development and share more logic across platforms.

#### 1. Adopt `web_core.GenericBinder`
Currently, the Angular `ComponentBinder` is a manual implementation. We should replace it with the shared `GenericBinder` from `web_core`.
* **Parity:** Shares 100% of complex binding logic (recursion, action wrapping, validation aggregation) with the React renderer.
* **Integration:** `ComponentHostComponent` instantiates the binder and maps its snapshot to a single Angular Signal.

#### 2. Strongly Typed Component API
Move away from `Record<string, BoundProperty>` and use the `ResolveA2uiProps<T>` type.
* **Benefit:** Full IDE auto-complete for `props().variant`, `props().action()`, and auto-generated setters like `props().setValue('val')`.

#### 3. Example: Revised Component Structure
A revised component becomes significantly cleaner, with zero boilerplate for data model synchronization and validation:

```typescript
@Component({
  selector: 'a2ui-v09-text-field',
  template: `
    <div class="field-container">
      <label>{{ props().label }}</label>
      <input
        [type]="props().variant === 'obscured' ? 'password' : 'text'"
        [value]="props().value"
        (input)="props().setValue($any($event.target).value)"
        [class.invalid]="props().isValid === false" />

      @if (props().validationErrors?.[0]; as error) {
        <span class="error-text">{{ error }}</span>
      }
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TextFieldComponent {
  // Provided as a Signal by the host component/adapter
  @Input({ required: true }) props!: Signal<ResolveA2uiProps<typeof TextFieldApi>>;
}
```

#### 4. Simplified Child Rendering
Create a dedicated `A2uiChild` component that consumes the `STRUCTURAL` metadata from the binder.
* **The Binder's Role:** The `GenericBinder` resolves `ChildList` properties into a list of `{ id: string, basePath: string }` objects.
* **Template Pattern:**
  ```html
  <!-- Column Component -->
  <div class="column">
    @for (childMeta of props().children; track childMeta.basePath) {
      <a2ui-v09-child [meta]="childMeta" />
    }
  </div>
  ```
* **DI for Context:** Use Angular Dependency Injection to provide `surfaceId` at the root, removing the need to pass it as an `@Input` through every layer.

---

### Performance Rationale: Why the Single Signal Approach?

A common concern with a single signal (`props()`) instead of per-property signals is reduced granularity. However, this approach is optimal for A2UI for the following reasons:

1. **Component Scale:** A2UI components are typically small "Atoms" (2–10 props). Re-running a template check for 10 properties takes microseconds—far less than the memory/CPU overhead of managing 10 separate Signal subscriptions and bridges per component instance.
2. **DOM Stability:** Even if the `props()` signal fires and the template re-runs, Angular’s renderer only touches the real DOM for the specific attributes that actually changed.
3. **The Structural Boundary:** The most expensive part of rendering is the **Component Tree**. Because structural properties are handled by the binder, if a child's text changes, the parent (e.g., a `Column`) re-evaluates but passes the *same* metadata to its other children. Angular's `OnPush` and input checking prevent those siblings from re-rendering or re-binding.
4. **Escape Hatches:** For exceptionally heavy components, granularity can be regained using `computed` signals inside the component logic:
   ```typescript
   data = computed(() => this.props().heavyData); // Only fires when data actually changes
   ```

This pattern significantly improves developer experience and logic sharing without sacrificing real-world performance.