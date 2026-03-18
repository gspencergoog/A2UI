import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Divider } from './divider';
import { Theme } from '../rendering/theming';
import { MessageProcessor } from '../data/processor';
import { Types } from '../types';

describe('Divider Component', () => {
  let component: Divider;
  let fixture: ComponentFixture<Divider>;
  let mockTheme: Theme;

  const mockNode: Types.DividerNode = {
    id: 'div-1',
    type: 'Divider',
    weight: 1,
    properties: {},
  };

  beforeEach(async () => {
    mockTheme = new Theme();
    mockTheme.components = { Divider: 'divider-class' } as any;

    await TestBed.configureTestingModule({
      imports: [Divider],
      providers: [
        { provide: Theme, useValue: mockTheme },
        { provide: MessageProcessor, useValue: {} },
      ],
    })
    .compileComponents();

    fixture = TestBed.createComponent(Divider);
    component = fixture.componentInstance;
    
    fixture.componentRef.setInput('surfaceId', 'surface-1');
    fixture.componentRef.setInput('component', mockNode);
    fixture.componentRef.setInput('weight', 1);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should apply theme class', () => {
    const hrEl = fixture.nativeElement.querySelector('hr');
    expect(hrEl.className).toContain('divider-class');
  });
});
