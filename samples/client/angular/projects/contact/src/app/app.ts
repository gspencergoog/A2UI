/*
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { A2uiRendererService, SurfaceComponent } from '@a2ui/angular/v0_9';
import { Client } from './client';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: 'app.css',
  imports: [SurfaceComponent, CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  protected client = inject(Client);
  protected renderer = inject(A2uiRendererService);

  protected hasData = signal(false);
  protected surfaceIds = signal<string[]>([]);

  constructor() {
    // Initial surfaces
    this.surfaceIds.set(Array.from(this.renderer.surfaceGroup.surfacesMap.keys()));

    // Keep surface list in sync
    this.renderer.surfaceGroup.onSurfaceCreated.subscribe((surface) => {
      this.surfaceIds.update((ids) => [...ids, surface.id]);
    });
    this.renderer.surfaceGroup.onSurfaceDeleted.subscribe((id) => {
      this.surfaceIds.update((ids) => ids.filter((sid) => sid !== id));
    });

    // Bridge messages to renderer
    this.client.messages$.subscribe((messages) => {
      this.renderer.processMessages(messages);
    });
  }

  protected async handleSubmit(event: SubmitEvent) {
    event.preventDefault();

    if (!(event.target instanceof HTMLFormElement)) {
      return;
    }

    const data = new FormData(event.target);
    const body = data.get('body') ?? null;

    if (body) {
      await this.client.makeRequest(body as string);
      this.hasData.set(true);
    }
  }
}
