import { TestBed } from '@angular/core/testing';
import { AgentStubService } from './agent-stub.service';
import { A2uiRendererService } from '@a2ui/angular/v0_9';
import { ActionDispatcher } from './action-dispatcher.service';
import { Subject } from 'rxjs';
import { A2uiMessage } from '@a2ui/web_core/v0_9';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('AgentStubService', () => {
  let service: AgentStubService;
  let mockRendererService: any;
  let mockActionDispatcher: any;
  let mockSurfaceGroup: any;

  beforeEach(() => {
    mockSurfaceGroup = {
      getSurface: vi.fn(),
    };
    mockRendererService = {
      processMessages: vi.fn(),
      get surfaceGroup() {
        return mockSurfaceGroup;
      },
    };
    mockActionDispatcher = {
      actions: new Subject(),
    };

    TestBed.configureTestingModule({
      providers: [
        AgentStubService,
        { provide: A2uiRendererService, useValue: mockRendererService },
        { provide: ActionDispatcher, useValue: mockActionDispatcher },
      ],
    });
    service = TestBed.inject(AgentStubService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('initializeDemo', () => {
    it('should send deleteSurface before createSurface if surface already exists', () => {
      const surfaceId = 'test-surface';
      const createMsg: A2uiMessage = {
        version: 'v0.9',
        createSurface: {
          surfaceId,
          catalogId: 'basic',
        },
      };
      const messages = [createMsg];

      // 1. First call: Surface does not exist
      mockSurfaceGroup.getSurface.mockReturnValue(undefined);
      service.initializeDemo(messages);

      // Should have called processMessages with initial messages only
      expect(mockRendererService.processMessages).toHaveBeenCalledWith(messages);
      expect(mockRendererService.processMessages).toHaveBeenCalledTimes(1);
      mockRendererService.processMessages.mockClear();

      // 2. Second call: Surface now exists
      mockSurfaceGroup.getSurface.mockReturnValue({ id: surfaceId });
      service.initializeDemo(messages);

      // Should have called processMessages twice:
      // First with deleteSurface, then with initial messages
      expect(mockRendererService.processMessages).toHaveBeenCalledTimes(2);
      expect(mockRendererService.processMessages).toHaveBeenNthCalledWith(1, [
        {
          version: 'v0.9',
          deleteSurface: { surfaceId },
        },
      ]);
      expect(mockRendererService.processMessages).toHaveBeenNthCalledWith(2, messages);
    });

    it('should NOT send deleteSurface if surface does not exist', () => {
      const surfaceId = 'new-surface';
      const createMsg: A2uiMessage = {
        version: 'v0.9',
        createSurface: {
          surfaceId,
          catalogId: 'basic',
        },
      };
      const messages = [createMsg];

      mockSurfaceGroup.getSurface.mockReturnValue(undefined);
      service.initializeDemo(messages);

      expect(mockRendererService.processMessages).toHaveBeenCalledTimes(1);
      expect(mockRendererService.processMessages).toHaveBeenCalledWith(messages);
    });
  });
});
