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

import { inputBinding } from '@angular/core';
import { Types } from '../types';
import { Catalog, CatalogEntries } from '../rendering/catalog';
import { BASIC_FUNCTIONS } from '@a2ui/web_core/v0_9/basic_catalog';

export const CATALOG: Catalog = new (class extends Catalog {
  readonly entries: CatalogEntries = {
  Row: {
    type: () => import('../components/row').then((r) => r.Row),
    bindings: (node) => {
      const properties = (node as Types.RowNode).properties;
      return [
        inputBinding('align', () => properties.align ?? 'start'),
        inputBinding('justify', () => properties.justify ?? 'start'),
      ];
    },
  },

  Column: {
    type: () => import('../components/column').then((r) => r.Column),
    bindings: (node) => {
      const properties = (node as Types.ColumnNode).properties;
      return [
        inputBinding('align', () => properties.align ?? 'start'),
        inputBinding('justify', () => properties.justify ?? 'start'),
      ];
    },
  },

  List: {
    type: () => import('../components/list').then((r) => r.List),
    bindings: (node) => {
      const properties = (node as Types.ListNode).properties;
      return [inputBinding('direction', () => properties.direction ?? 'vertical')];
    },
  },

  Card: () => import('../components/card').then((r) => r.Card),

  Image: {
    type: () => import('../components/image').then((r) => r.Image),
    bindings: (node) => {
      const properties = (node as Types.ImageNode).properties;
      return [
        inputBinding('url', () => properties.url),
        inputBinding('variant', () => properties.variant ?? 'icon'),
        inputBinding('fit', () => properties.fit ?? 'cover'),
      ];
    },
  },

  Icon: {
    type: () => import('../components/icon').then((r) => r.Icon),
    bindings: (node) => {
      const properties = (node as Types.IconNode).properties;
      return [inputBinding('name', () => properties.name)];
    },
  },

  Video: {
    type: () => import('../components/video').then((r) => r.Video),
    bindings: (node) => {
      const properties = (node as Types.VideoNode).properties;
      return [inputBinding('url', () => properties.url)];
    },
  },

  AudioPlayer: {
    type: () => import('../components/audio').then((r) => r.Audio),
    bindings: (node) => {
      const properties = (node as Types.AudioPlayerNode).properties;
      return [inputBinding('url', () => properties.url)];
    },
  },

  Text: {
    type: () => import('../components/text').then((r) => r.Text),
    bindings: (node) => {
      const properties = (node as Types.TextNode).properties;
      return [
        inputBinding('text', () => properties.text),
      ];
    },
  },

  Button: {
    type: () => import('../components/button').then((r) => r.Button),
    bindings: (node) => {
      const properties = (node as Types.ButtonNode).properties;
      return [
        inputBinding('action', () => properties.action),
        inputBinding('primary', () => properties.primary),
      ];
    },
  },

  Divider: () => import('../components/divider').then((r) => r.Divider),

  MultipleChoice: {
    type: () => import('../components/multiple-choice').then((r) => r.MultipleChoice),
    bindings: (node) => {
      const properties = (node as Types.MultipleChoiceNode).properties;
      return [
        inputBinding('options', () => properties.options || []),
        inputBinding('value', () => properties.value),
        inputBinding('description', () => 'Select an item'), // TODO: this should be defined in the properties
      ];
    },
  },

  TextField: {
    type: () => import('../components/text-field').then((r) => r.TextField),
    bindings: (node) => {
      const properties = (node as Types.TextFieldNode).properties;
      return [
        inputBinding('text', () => properties.value ?? null),
        inputBinding('label', () => properties.label),
        inputBinding('variant', () => properties.variant),
      ];
    },
  },

  DateTimeInput: {
    type: () => import('../components/datetime-input').then((r) => r.DatetimeInput),
    bindings: (node) => {
      const properties = (node as Types.DateTimeInputNode).properties;
      return [
        inputBinding('enableDate', () => properties.enableDate),
        inputBinding('enableTime', () => properties.enableTime),
        inputBinding('value', () => properties.value),
      ];
    },
  },

  CheckBox: {
    type: () => import('../components/checkbox').then((r) => r.Checkbox),
    bindings: (node) => {
      const properties = (node as Types.CheckboxNode).properties;
      return [
        inputBinding('label', () => properties.label),
        inputBinding('value', () => properties.value),
      ];
    },
  },

  Slider: {
    type: () => import('../components/slider').then((r) => r.Slider),
    bindings: (node) => {
      const properties = (node as Types.SliderNode).properties;
      return [
        inputBinding('value', () => properties.value),
        inputBinding('minValue', () => properties.min),
        inputBinding('maxValue', () => properties.max),
        inputBinding('label', () => ''), // TODO: this should be defined in the properties
      ];
    },
  },

  Tabs: {
    type: () => import('../components/tabs').then((r) => r.Tabs),
    bindings: (node) => {
      const properties = (node as Types.TabsNode).properties;
      return [inputBinding('tabs', () => properties.tabs)];
    },
  },

  Modal: {
    type: () => import('../components/modal').then((r) => r.Modal),
    bindings: () => [],
  },
};
})('https://a2ui.org/specification/v0_9/basic_catalog.json', [], BASIC_FUNCTIONS);

export const V0_9_CATALOG = CATALOG;
