import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TextField } from './text-field';
import { MessageProcessor } from '../data/processor';
import { Theme } from '../rendering/theming';
import { Catalog } from '../rendering/catalog';
import { Types } from '../types';
import { By } from '@angular/platform-browser';
import { ChangeDetectionStrategy } from '@angular/core';

describe('TextField Component', () => {
  let component: TextField;
  let fixture: ComponentFixture<TextField>;
  let mockTheme: Theme;
  let mockProcessor: jasmine.SpyObj<MessageProcessor>;

  beforeEach(async () => {
    mockTheme = new Theme();
    mockTheme.components = {
      TextField: {
        container: 'tf-container',
        label: 'tf-label',
        element: 'tf-input',
      },
    } as any;

    mockProcessor = jasmine.createSpyObj('MessageProcessor', ['dispatch', 'resolvePath', 'getData']);
    mockProcessor.dispatch.and.returnValue(Promise.resolve([]));

    await TestBed.configureTestingModule({
      imports: [TextField],
      providers: [
        { provide: MessageProcessor, useValue: mockProcessor },
        { provide: Theme, useValue: mockTheme },
        { provide: Catalog, useValue: {} },
      ],
    })
    .overrideComponent(TextField, {
      set: {
        changeDetection: ChangeDetectionStrategy.Default,
      }
    })
    .compileComponents();

    fixture = TestBed.createComponent(TextField);
    component = fixture.componentInstance;
    
    fixture.componentRef.setInput('surfaceId', 'surface-1');
    fixture.componentRef.setInput('component', { id: 'tf-1', type: 'TextField', weight: 1 });
    fixture.componentRef.setInput('weight', 1);
    fixture.componentRef.setInput('label', { literalString: 'Name' });
    fixture.componentRef.setInput('text', { literalString: 'John Doe' });

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render label and set input attributes', () => {
    const labelEl = fixture.debugElement.query(By.css('label'));
    expect(labelEl).toBeTruthy();
    expect(labelEl.nativeElement.textContent.trim()).toBe('Name');

    const inputEl = fixture.debugElement.query(By.css('input'));
    expect(inputEl).toBeTruthy();
    expect(inputEl.nativeElement.value).toBe('John Doe');
    expect(inputEl.nativeElement.type).toBe('text'); // Default
  });

  it('should change input type based on textFieldType', () => {
    fixture.componentRef.setInput('textFieldType', 'number');
    fixture.detectChanges();
    
    const inputEl = fixture.debugElement.query(By.css('input'));
    expect(inputEl.nativeElement.type).toBe('number');

    fixture.componentRef.setInput('textFieldType', 'date');
    fixture.detectChanges();
    expect(inputEl.nativeElement.type).toBe('date');
  });

  it('should trigger sendAction on input update', async () => {
    const inputEl = fixture.debugElement.query(By.css('input'));
    expect(inputEl).toBeTruthy();

    inputEl.nativeElement.value = 'Jane Doe';
    inputEl.nativeElement.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(mockProcessor.dispatch).toHaveBeenCalled();
    const message = mockProcessor.dispatch.calls.mostRecent().args[0];
    expect(message.userAction).toBeTruthy();
    expect(message.userAction!.name).toBe('input');
    expect(message.userAction!.context).toEqual({ value: 'Jane Doe' });
  });
});
