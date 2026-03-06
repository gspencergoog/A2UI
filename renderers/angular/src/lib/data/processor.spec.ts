import { TestBed } from '@angular/core/testing';
import { MessageProcessor, A2uiClientMessage } from './processor';
import { Types } from '../types';
import { Catalog } from '../rendering/catalog';


describe('MessageProcessor', () => {
  let service: MessageProcessor;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{ provide: Catalog, useValue: {} }],
    });
    service = TestBed.inject(MessageProcessor);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should update surface model on createSurface/updateComponents', () => {
    const surfaceId = 'test-surface';
    const initMsg: Types.ServerToClientMessage = {
      createSurface: {
        surfaceId,
        catalogId: 'https://a2ui.org/specification/v0_9/basic_catalog.json',
        theme: {},
      },
      version: 'v0.9',
    } as any;

    service.processMessages([initMsg]);

    service.processMessages([
      {
        updateComponents: {
          surfaceId,
          components: [{ id: 'root', component: 'Box', children: [] }],
        },
        version: 'v0.9',
      },
    ] as any);

    const surface = service.getSurfaces().get(surfaceId);
    expect(surface).toBeTruthy();
    expect(surface?.componentsModel.get('root')).toBeTruthy();
  });

  it('should update data model on updateDataModel', () => {
    const surfaceId = 'test-surface';
    service.processMessages([
      {
        createSurface: {
          surfaceId,
          catalogId: 'https://a2ui.org/specification/v0_9/basic_catalog.json',
        },
        version: 'v0.9',
      },
    ] as any);

    service.processMessages([
      {
        updateDataModel: {
          surfaceId,
          path: '/foo',
          value: 'bar',
        },
        version: 'v0.9',
      },
    ] as any);

    const surface = service.getSurfaces().get(surfaceId);
    expect(surface).toBeTruthy();
    expect(surface?.dataModel.get('/foo')).toBe('bar');
  });

  it('should merge component updates correctly', () => {
    const surfaceId = 's1';
    service.processMessages([
      {
        createSurface: {
          surfaceId,
          catalogId: 'https://a2ui.org/specification/v0_9/basic_catalog.json',
        },
        version: 'v0.9',
      },
    ] as any);

    service.processMessages([
      {
        updateComponents: {
          surfaceId,
          components: [
            { id: 'root', component: 'Box', children: ['childA'] },
            { id: 'childA', component: 'Text', text: 'Old Text' },
          ],
        },
        version: 'v0.9',
      },
    ] as any);

    let surface = service.getSurfaces().get(surfaceId);
    expect(surface?.componentsModel.get('childA')?.properties['text']).toBe('Old Text');

    service.processMessages([
      {
        updateComponents: {
          surfaceId,
          components: [{ id: 'childA', component: 'Text', text: 'New Text' }],
        },
        version: 'v0.9',
      },
    ] as any);

    surface = service.getSurfaces().get(surfaceId);
    expect(surface?.componentsModel.get('childA')?.properties['text']).toBe('New Text');
  });

  it('should handle deleteSurface', () => {
    const surfaceId = 's1';
    service.processMessages([
      {
        createSurface: {
          surfaceId,
          catalogId: 'https://a2ui.org/specification/v0_9/basic_catalog.json',
        },
        version: 'v0.9',
      },
    ] as any);

    expect(service.getSurfaces().get(surfaceId)).toBeTruthy();

    service.processMessages([
      {
        deleteSurface: {
          surfaceId,
        },
        version: 'v0.9',
      },
    ] as any);

    expect(service.getSurfaces().get(surfaceId)).toBeUndefined();
  });


  it('should emit action on events subject', (done) => {
    const surfaceId = 's1';
    service.processMessages([
      {
        createSurface: {
          surfaceId,
          catalogId: 'https://a2ui.org/specification/v0_9/basic_catalog.json',
        },
        version: 'v0.9',
      } as any,
    ]);

    const action: A2uiClientMessage = {
      version: 'v0.9',
      action: {
        name: 'submit',
        surfaceId: 's1',
        sourceComponentId: 'button1',
        timestamp: new Date().toISOString(),
        context: { foo: 'bar' },
      },
    };

    service.events.subscribe((event) => {
      expect(event.message).toEqual(action);
      done();
    });

    service.dispatch(action);
  });
});
