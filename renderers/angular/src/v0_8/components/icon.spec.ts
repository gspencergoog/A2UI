import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Icon } from './icon';
import { MessageProcessor } from '../data/processor';
import { Theme } from '../rendering/theming';
import { Catalog } from '../rendering/catalog';
import { Types } from '../types';
import { By } from '@angular/platform-browser';

describe('Icon Component', () => {
  let component: Icon;
  let fixture: ComponentFixture<Icon>;
  let mockTheme: Theme;

  beforeEach(async () => {
    mockTheme = new Theme();
    mockTheme.components = { Icon: 'icon-class' } as any;

    await TestBed.configureTestingModule({
      imports: [Icon],
      providers: [
        { provide: MessageProcessor, useValue: { resolvePrimitive: (p: any) => p?.literalString || p } },
        { provide: Theme, useValue: mockTheme },
        { provide: Catalog, useValue: {} },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Icon);
    component = fixture.componentInstance;
    
    fixture.componentRef.setInput('surfaceId', 'surface-1');
    fixture.componentRef.setInput('component', { id: 'icon-1', type: 'Icon', weight: 1 });
    fixture.componentRef.setInput('weight', 1);
    fixture.componentRef.setInput('name', null);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render icon name inside span if provided', () => {
    fixture.componentRef.setInput('name', { literalString: 'home' });
    fixture.detectChanges();

    const spanEl = fixture.debugElement.query(By.css('.g-icon'));
    expect(spanEl).toBeTruthy();
    expect(spanEl.nativeElement.textContent).toBe('home');
    
    const sectionEl = fixture.debugElement.query(By.css('section'));
    expect(sectionEl).toBeTruthy();
    expect(sectionEl.nativeElement.className).toBe('icon-class');
  });

  it('should NOT render anything if name is null', () => {
    fixture.componentRef.setInput('name', null);
    fixture.detectChanges();

    const spanEl = fixture.debugElement.query(By.css('.g-icon'));
    expect(spanEl).toBeFalsy();
    
    const sectionEl = fixture.debugElement.query(By.css('section'));
    expect(sectionEl).toBeFalsy();
  });
});
