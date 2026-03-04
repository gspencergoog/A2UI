import assert from 'node:assert';
import { test, describe, it, beforeEach, mock } from 'node:test';
import { SurfaceModel } from './surface-model.js';
import { Catalog, ComponentApi } from '../catalog/types.js';
import { ComponentModel } from './component-model.js';
import { ComponentContext } from '../rendering/component-context.js';

describe('SurfaceModel', () => {
  let surface: SurfaceModel<ComponentApi>;
  let catalog: Catalog<ComponentApi>;
  let actions: any[] = [];

  beforeEach(() => {
    actions = [];
    catalog = new Catalog('test-catalog', []);
    surface = new SurfaceModel<ComponentApi>('surface-1', catalog, {});
    surface.onAction.subscribe(async (action) => {
      actions.push(action);
    });
  });

  it('initializes with empty data model', () => {
    assert.deepStrictEqual(surface.dataModel.get('/'), {});
  });

  it('exposes components model', () => {
    surface.componentsModel.addComponent(new ComponentModel('c1', 'Button', {}));
    assert.ok(surface.componentsModel.get('c1'));
  });

  it('dispatches actions', async () => {
    await surface.dispatchAction({ type: 'click' });
    assert.strictEqual(actions.length, 1);
    assert.strictEqual(actions[0].type, 'click');
  });

  it('creates a component context', () => {
    surface.componentsModel.addComponent(new ComponentModel('root', 'Box', {}));
    const ctx = new ComponentContext(surface, 'root', '/mydata');
    assert.ok(ctx);
    assert.strictEqual(ctx.dataContext.path, '/mydata');
  });

  it('disposes resources', () => {
    // We can verify dispose by checking if listeners are removed or internal state is cleared.
    // Since DataModel and SurfaceComponentsModel also have dispose, we assume they are called.
    // A simple check is to ensure we can call dispose without error,
    // and perhaps check side effects if possible (e.g. mocked dependencies).
    // For now, we'll verify it doesn't throw and maybe check a property if accessible.

    // To be more thorough, we could mock the dependencies, but they are hardcoded in constructor.
    // Let's at least verify onAction is disposed.

    let actionReceived = false;
    const sub = surface.onAction.subscribe(() => { actionReceived = true; });

    surface.dispose();

    // After dispose, onAction should probably not emit or subscriptions should be cleared.
    // The current EventEmitter implementation clears listeners on dispose?
    // Let's check EventEmitter implementation again if needed, but assuming standard behavior:

    // dispatchAction might throw or do nothing after dispose depending on implementation.
    // The current implementation of EventEmitter.dispose just clears listeners.

    surface.dispatchAction({ type: 'click' });
    assert.strictEqual(actionReceived, false, 'Should not receive actions after dispose');
  });
});
