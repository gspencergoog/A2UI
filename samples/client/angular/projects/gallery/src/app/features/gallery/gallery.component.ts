/*
 Copyright 2025 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

import { ChangeDetectionStrategy, Component, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Catalog, Surface, Theme } from '@a2ui/angular';
import { DataModel, SurfaceComponentsModel, SurfaceModel } from '@a2ui/web_core/v0_9';
import { ComponentModel } from '@a2ui/web_core/v0_9';
import * as Types from '@a2ui/web_core/types/types';
import { inject } from '@angular/core';

interface GallerySample {
  id: string;
  title: string;
  description: string;
  surface: SurfaceModel<any>;
}

@Component({
  selector: 'app-gallery',
  imports: [CommonModule, Surface],
  templateUrl: './gallery.html',
  styleUrl: './gallery.css',
  changeDetection: ChangeDetectionStrategy.Eager,
})
export class GalleryComponent {
  private readonly catalog = inject(Catalog);
  private readonly theme = inject(Theme);

  @ViewChild('dialog') dialog!: ElementRef<HTMLDialogElement>;
  selectedSample: GallerySample | null = null;
  activeSection = 'welcome';
  showJsonId: string | null = null;

  samples: GallerySample[] = [
    {
      id: 'photo-list',
      title: 'List of items',
      description: 'List of items with images',
      surface: this.createSingleComponentSurface('Card', {
        child: this.createComponent('Column', {
          children: [
            this.createComponent('Row', {
              children: [
                this.createComponent('Image', {
                  url: { literalString: 'https://picsum.photos/id/11/300/300' },
                }),
                this.createComponent('Column', {
                  children: [
                    this.createComponent('Text', {
                      text: {
                        literalString: 'A misty, serene natural landscape.',
                      },
                    }),
                  ],
                }),
              ],
            }),
            this.createComponent('Row', {
              children: [
                this.createComponent('Image', {
                  url: { literalString: 'https://picsum.photos/id/12/300/300' },
                }),
                this.createComponent('Column', {
                  children: [
                    this.createComponent('Text', {
                      text: {
                        literalString:
                          'A river flows through marsh toward hazy, forested mountains.',
                      },
                    }),
                  ],
                }),
              ],
            }),
            this.createComponent('Row', {
              children: [
                this.createComponent('Image', {
                  url: { literalString: 'https://picsum.photos/id/13/300/300' },
                }),
                this.createComponent('Text', {
                  text: {
                    literalString:
                      'Large dark rocks overlook sandy beach and ocean with distant islands.',
                  },
                }),
              ],
            }),
          ],
        }),
      }),
    },
    {
      id: 'welcome',
      title: 'Welcome Card',
      description: 'A simple welcome card with an image and text.',
      surface: this.createSingleComponentSurface('Card', {
        child: this.createComponent('Column', {
          children: [
            this.createComponent('Image', {
              url: { literalString: 'https://picsum.photos/id/10/600/300' },
            }),
            this.createComponent('Text', {
              text: {
                literalString:
                  'Explore the possibilities of A2UI components with this interactive gallery.',
              },
            }),
            this.createComponent('Button', {
              action: { type: 'submit' },
              child: this.createComponent('Text', { text: { literalString: 'Get Started' } }),
            }),
          ],
          alignment: 'center',
        }),
      }),
    },
    {
      id: 'form',
      title: 'Contact Form',
      description: 'A sample contact form with validation.',
      surface: this.createSingleComponentSurface('Card', {
        child: this.createComponent('Column', {
          children: [
            this.createComponent('Row', {
              children: [
                this.createComponent('TextField', {
                  label: { literalString: 'Name' },
                  type: 'text',
                  text: { literalString: '' },
                }),
              ],
            }),
            this.createComponent('Row', {
              children: [
                this.createComponent('TextField', {
                  label: { literalString: 'Email Address' },
                  type: 'email',
                  text: { literalString: '' },
                }),
              ],
            }),
            this.createComponent('Row', {
              children: [
                this.createComponent('TextField', {
                  label: { literalString: 'Message' },
                  text: { literalString: '' },
                }),
              ],
            }),
            this.createComponent('Button', {
              action: { type: 'submit' },
              child: this.createComponent('Text', { text: { literalString: 'Send Message' } }),
            }),
          ],
        }),
      }),
    },
  ];

  openDialog(sample: GallerySample) {
    this.selectedSample = sample;
    this.dialog.nativeElement.showModal();
  }

  closeDialog() {
    this.dialog.nativeElement.close();
  }

  scrollTo(id: string) {
    this.activeSection = id;
    const element = document.getElementById('section-' + id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  onScroll(event: Event) {
    const container = event.target as HTMLElement;
    const sections = container.querySelectorAll('.component-section');

    let current = '';
    const containerTop = container.scrollTop;

    for (let i = 0; i < sections.length; i++) {
      const section = sections[i] as HTMLElement;
      const sectionTop = section.offsetTop - container.offsetTop;

      if (sectionTop <= containerTop + 100) {
        const id = section.getAttribute('id');
        if (id) {
          current = id.replace('section-', '');
        }
      }
    }

    if (current && current !== this.activeSection) {
      this.activeSection = current;
    }
  }

  toggleJson(id: string) {
    this.showJsonId = this.showJsonId === id ? null : id;
  }

  getJson(surface: SurfaceModel<any>): string {
    return JSON.stringify(
      {
        id: surface.id,
        components: Object.fromEntries(surface.componentsModel.entries),
      },
      null,
      2,
    );
  }

  /*
    Recursively flattens a nested component definition into a flat map,
    returning the ID of the processed component.
  */
  private flatten(
    componentDef: { id: string; type: string; properties: any },
    componentsModel: SurfaceComponentsModel,
  ): string {
    const flattenedProps: any = { ...componentDef.properties };

    const processChild = (childDef: any): string => {
      if (childDef && typeof childDef === 'object' && childDef.type) {
        return this.flatten(childDef, componentsModel);
      }
      return childDef;
    };

    if (flattenedProps.child) {
      flattenedProps.child = processChild(flattenedProps.child);
    }
    if (Array.isArray(flattenedProps.children)) {
      flattenedProps.children = flattenedProps.children.map((child: any) => processChild(child));
    }
    if (flattenedProps.entryPointChild) {
      flattenedProps.entryPointChild = processChild(flattenedProps.entryPointChild);
    }
    if (flattenedProps.contentChild) {
      flattenedProps.contentChild = processChild(flattenedProps.contentChild);
    }
    if (Array.isArray(flattenedProps.tabItems)) {
      flattenedProps.tabItems = flattenedProps.tabItems.map((item: any) => ({
        ...item,
        child: processChild(item.child),
      }));
    }

    const componentModel = new ComponentModel(componentDef.id, componentDef.type, flattenedProps);
    componentsModel.addComponent(componentModel);
    return componentDef.id;
  }

  private createSingleComponentSurface(type: string, properties: any): SurfaceModel<any> {
    const rootId = 'root';
    const surfaceId = 'generated-' + Math.random().toString(36).substr(2, 9);
    const model = new SurfaceModel(surfaceId, this.catalog as any, this.theme);

    const rootDef = {
      id: rootId,
      type: type,
      properties: properties,
    };

    this.flatten(rootDef, model.componentsModel);

    return model;
  }

  private createComponent(type: string, properties: any): any {
    return {
      id: 'generated-' + Math.random().toString(36).substr(2, 9),
      type: type,
      properties: properties,
    };
  }
}
