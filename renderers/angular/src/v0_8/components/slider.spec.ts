import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Slider } from './slider';
import { MessageProcessor } from '../data/processor';
import { Theme } from '../rendering/theming';
import { Catalog } from '../rendering/catalog';
import { Types } from '../types';
import { By } from '@angular/platform-browser';
import { ChangeDetectionStrategy } from '@angular/core';

describe('Slider Component', () => {
  let component: Slider;
  let fixture: ComponentFixture<Slider>;
  let mockTheme: Theme;
  let mockProcessor: jasmine.SpyObj<MessageProcessor>;

  beforeEach(async () => {
    mockTheme = new Theme();
    mockTheme.components = {
      Slider: {
        container: 'slider-container',
        label: 'slider-label',
        element: 'slider-input',
      },
    } as any;

    mockProcessor = jasmine.createSpyObj('MessageProcessor', ['dispatch', 'resolvePath', 'getData']);
    mockProcessor.dispatch.and.returnValue(Promise.resolve([]));

    await TestBed.configureTestingModule({
      imports: [Slider],
      providers: [
        { provide: MessageProcessor, useValue: mockProcessor },
        { provide: Theme, useValue: mockTheme },
        { provide: Catalog, useValue: {} },
      ],
    })
    .overrideComponent(Slider, {
      set: {
        changeDetection: ChangeDetectionStrategy.Default,
      }
    })
    .compileComponents();

    fixture = TestBed.createComponent(Slider);
    component = fixture.componentInstance;
    
    fixture.componentRef.setInput('surfaceId', 'surface-1');
    fixture.componentRef.setInput('component', { id: 'slider-1', type: 'Slider', weight: 1 });
    fixture.componentRef.setInput('weight', 1);
    fixture.componentRef.setInput('label', { literalString: 'Volume' });
    fixture.componentRef.setInput('value', { literalNumber: 50 });
    fixture.componentRef.setInput('minValue', 0);
    fixture.componentRef.setInput('maxValue', 100);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render label and set input attributes', () => {
    const labelEl = fixture.debugElement.query(By.css('label'));
    expect(labelEl).toBeTruthy();
    expect(labelEl.nativeElement.textContent.trim()).toBe('Volume');

    const inputEl = fixture.debugElement.query(By.css('input[type="range"]'));
    expect(inputEl).toBeTruthy();
    expect(inputEl.nativeElement.value).toBe('50');
    expect(inputEl.nativeElement.min).toBe('0');
    expect(inputEl.nativeElement.max).toBe('100');
  });

  it('should trigger sendAction with number context on input change', async () => {
    const inputEl = fixture.debugElement.query(By.css('input[type="range"]'));
    expect(inputEl).toBeTruthy();

    inputEl.nativeElement.value = '75';
    inputEl.nativeElement.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(mockProcessor.dispatch).toHaveBeenCalled();
    const message = mockProcessor.dispatch.calls.mostRecent().args[0];
    expect(message.userAction).toBeTruthy();
    expect(message.userAction!.name).toBe('change');
    expect(message.userAction!.context).toEqual({ value: 75 });
  });
});
