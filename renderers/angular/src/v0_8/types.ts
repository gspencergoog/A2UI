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

import * as WebCore from '@a2ui/web_core/v0_8';

export namespace Types {
  export type Action = WebCore.Action;
  export type FunctionCall = unknown; // v0.8 might not have FunctionCall or structure differs
  export type SurfaceID = string;

  export interface ClientToServerMessage {
    action: Action;
    version: string;
    surfaceId?: string;
  }
  export type A2UIClientEventMessage = ClientToServerMessage;

  export interface Component<P = Record<string, unknown>> {
    id: string;
    type: string;
    properties: P;
  }

  export type AnyComponentNode = Component<any>;
  export type CustomNode = AnyComponentNode;

  export type ServerToClientMessage = WebCore.ServerToClientMessage;

  export interface Theme {
    components?: Record<string, unknown>;
    additionalStyles?: string[];
  }

  // Aliases
  export type Row = WebCore.RowNode;
  export type Column = WebCore.ColumnNode;
  export type Text = WebCore.TextNode;
  export type List = WebCore.ListNode;
  export type Image = WebCore.ImageNode;
  export type Icon = WebCore.IconNode;
  export type Video = WebCore.VideoNode;
  export type Audio = WebCore.AudioPlayerNode;
  export type Button = WebCore.ButtonNode;
  export type Divider = WebCore.DividerNode;
  export type MultipleChoice = WebCore.MultipleChoiceNode;
  export type TextField = WebCore.TextFieldNode;
  export type Checkbox = WebCore.CheckboxNode;
  export type Slider = WebCore.SliderNode;
  export type DateTimeInput = WebCore.DateTimeInputNode;
  export type Tabs = WebCore.TabsNode;
  export type Modal = WebCore.ModalNode;

  // Explicit Node exports
  export type RowNode = WebCore.RowNode;
  export type ColumnNode = WebCore.ColumnNode;
  export type TextNode = WebCore.TextNode;
  export type ListNode = WebCore.ListNode;
  export type ImageNode = WebCore.ImageNode;
  export type IconNode = WebCore.IconNode;
  export type VideoNode = WebCore.VideoNode;
  export type AudioPlayerNode = WebCore.AudioPlayerNode;
  export type ButtonNode = WebCore.ButtonNode;
  export type DividerNode = WebCore.DividerNode;
  export type MultipleChoiceNode = WebCore.MultipleChoiceNode;
  export type TextFieldNode = WebCore.TextFieldNode;
  export type CheckboxNode = WebCore.CheckboxNode;
  export type SliderNode = WebCore.SliderNode;
  export type DateTimeInputNode = WebCore.DateTimeInputNode;
  export type TabsNode = WebCore.TabsNode;
  export type ModalNode = WebCore.ModalNode;

  export type CardNode = WebCore.CardNode;
}
