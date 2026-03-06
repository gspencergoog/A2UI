import { TestBed } from '@angular/core/testing';
import { provideA2UI } from './config';
import { Catalog, Theme } from './rendering';
import { DOCUMENT } from '@angular/common';

describe('provideA2UI', () => {
  it('should inject styles into head', async () => {
    // Clear any existing styles from previous tests to ensure isolation
    const existing = document.getElementById('a2ui-structural-styles');
    if (existing) {
      existing.remove();
    }

    const dummyCatalog: Catalog = {};
    const dummyTheme: Theme = { components: {}, additionalStyles: {} };

    await TestBed.configureTestingModule({
      providers: [
        provideA2UI({
          catalog: dummyCatalog,
          theme: dummyTheme,

          processor: {
            dispatch: () => Promise.resolve([]),
            getSurfaces: () => new Map(),
            events: { subscribe: () => {} },
          } as any,
        }),
      ],
    });

    // We don't need to inject anything specific, just bringing up the module should trigger APP_INITIALIZER
    // However, APP_INITIALIZER runs during initialization.
    // TestBed initializes on the first inject.
    TestBed.inject(DOCUMENT);

    const styleTag = document.getElementById('a2ui-structural-styles');
    expect(styleTag).toBeTruthy();
    expect(styleTag?.textContent).toContain('display: flex');
  });
});
