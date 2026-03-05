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

import {
  EnvironmentProviders,
  makeEnvironmentProviders,
  Provider,
  InjectionToken,
  Type,
  APP_INITIALIZER,
  inject,
  PLATFORM_ID,
} from '@angular/core';
import { DOCUMENT, isPlatformBrowser } from '@angular/common';
import { Catalog, Theme } from './rendering';
import { ExpressionEvaluator } from '@a2ui/web_core/v0_9/basic_catalog';
import { MessageProcessor } from '@a2ui/web_core/v0_9'; // Default type for now, but token can hold any
import { structuralStyles } from './rendering/styles';

/**
 * Injection token for a component to render when a catalog entry is not found.
 */
export const UNKNOWN_COMPONENT = new InjectionToken<Type<unknown>>('UNKNOWN_COMPONENT');

/**
 * Injection token for the Expression Evaluator.
 */
export const A2UI_EVALUATOR = new InjectionToken<ExpressionEvaluator>('A2UI_EVALUATOR');

/**
 * Injection token for the Message Processor.
 */
export const A2UI_PROCESSOR = new InjectionToken<unknown>('A2UI_PROCESSOR');

function initializeStyles() {
  const document = inject(DOCUMENT);
  const platformId = inject(PLATFORM_ID);

  if (isPlatformBrowser(platformId)) {
    const styleId = 'a2ui-structural-styles';
    if (!document.getElementById(styleId)) {
      const styles = document.createElement('style');
      styles.id = styleId;
      styles.textContent = structuralStyles;
      document.head.appendChild(styles);
    }
  }
}

/**
 * Configures the A2UI provider for the application.
 *
 * @param config The configuration object.
 * @param config.catalog The component catalog to use for rendering.
 * @param config.theme The theme definition.
 * @param config.evaluator The expression evaluator instance.
 * @param config.processor The message processor instance.
 * @param config.unknownComponent Optional component to render when a catalog entry is not found.
 * @returns The environment providers for A2UI.
 *
 * @example
 * ```typescript
 * bootstrapApplication(AppComponent, {
 *   providers: [
 *     provideA2UI({
 *       catalog: V0_9_CATALOG,
 *       theme: MY_THEME,
 *       evaluator: new ExpressionEvaluator(BASIC_FUNCTIONS),
 *       processor: new V09Processor(),
 *     }),
 *   ],
 * });
 * ```
 */
export function provideA2UI(config: {
  catalog: Catalog;
  theme: Theme;
  evaluator: ExpressionEvaluator;
  processor: unknown;
  unknownComponent?: Type<unknown>;
}): EnvironmentProviders {
  const providers: Provider[] = [
    { provide: Catalog, useValue: config.catalog },
    { provide: Theme, useValue: config.theme },
    { provide: A2UI_EVALUATOR, useValue: config.evaluator },
    { provide: A2UI_PROCESSOR, useValue: config.processor },
    config.unknownComponent
      ? { provide: UNKNOWN_COMPONENT, useValue: config.unknownComponent }
      : [],
    {
      provide: APP_INITIALIZER,
      useFactory: () => initializeStyles,
      multi: true,
    },
  ];

  return makeEnvironmentProviders(providers);
}
