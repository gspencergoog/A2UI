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

import { Types } from '../types';
import { InjectionToken } from '@angular/core';

/**
 * Injection token for the A2UI Theme.
 * Provide this token to configure the global theme for A2UI components.
 */
export const Theme = new InjectionToken<Theme>('Theme');

/**
 * Defines the theme structure for A2UI components.
 * This is an alias for the protocol's Theme type.
 */
export type Theme = Types.Theme;
