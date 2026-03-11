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

import {
  Action as WebCoreAction,
  FunctionCall as WebCoreFunctionCall,
  A2uiMessage,
} from '@a2ui/web_core/v0_9';

import {
  ButtonNode,
  TextNode,
  ImageNode,
  IconNode,
  AudioPlayerNode,
  VideoNode,
  CardNode,
  DividerNode,
  RowNode,
  ColumnNode,
  ListNode,
  TextFieldNode,
  CheckBoxNode,
  SliderNode,
  ChoicePickerNode,
  DateTimeInputNode,
  ModalNode,
  TabsNode,
} from '@a2ui/web_core/v0_9/basic_catalog';

export namespace Types {
  export type Action = WebCoreAction;
  export type FunctionCall = WebCoreFunctionCall;
  export type SurfaceID = string;

  export interface ClientToServerMessage {
    action: Action;
    version: string;
    surfaceId?: string;
  }
  export type A2UIClientEventMessage = ClientToServerMessage;

  // Base Component Node (Runtime Model)
  // This is kept here to not break legacy component definition structures if they exist 
  // alongside the imported ones. 
  export interface Component<P = Record<string, any>> {
    id: string;
    type: string;
    properties: P;
    [key: string]: any; // For flexibility and mixed-in metadata
  }

  export type AnyComponentNode = Component<any>;
  export type CustomNode = AnyComponentNode;

  export type ServerToClientMessage = A2uiMessage;

  export interface Theme {
    components?: any;
    additionalStyles?: any;
    [key: string]: any;
  }

  // Aliases for backward compatibility in Angular renderer
  // Most angular components refer to these types
  export type Row = RowNode;
  export type Column = ColumnNode;
  export type Text = TextNode;
  export type List = ListNode;
  export type Image = ImageNode;
  export type Icon = IconNode;
  export type Video = VideoNode;
  export type Audio = AudioPlayerNode;
  export type Button = ButtonNode;
  export type Divider = DividerNode;
  export type MultipleChoice = ChoicePickerNode;
  export type TextField = TextFieldNode;
  export type Checkbox = CheckBoxNode;
  export type CheckBox = CheckBoxNode;
  export type Slider = SliderNode;
  export type DateTimeInput = DateTimeInputNode;
  export type Tabs = TabsNode;
  export type Modal = ModalNode;
  export type ChoicePicker = ChoicePickerNode;
  
  // Explicit Node exports for backward compatibility
  export type RowNode = import('@a2ui/web_core/v0_9/basic_catalog').RowNode;
  export type ColumnNode = import('@a2ui/web_core/v0_9/basic_catalog').ColumnNode;
  export type TextNode = import('@a2ui/web_core/v0_9/basic_catalog').TextNode;
  export type ListNode = import('@a2ui/web_core/v0_9/basic_catalog').ListNode;
  export type ImageNode = import('@a2ui/web_core/v0_9/basic_catalog').ImageNode;
  export type IconNode = import('@a2ui/web_core/v0_9/basic_catalog').IconNode;
  export type VideoNode = import('@a2ui/web_core/v0_9/basic_catalog').VideoNode;
  export type AudioPlayerNode = import('@a2ui/web_core/v0_9/basic_catalog').AudioPlayerNode;
  export type ButtonNode = import('@a2ui/web_core/v0_9/basic_catalog').ButtonNode;
  export type DividerNode = import('@a2ui/web_core/v0_9/basic_catalog').DividerNode;
  export type MultipleChoiceNode = import('@a2ui/web_core/v0_9/basic_catalog').ChoicePickerNode;
  export type ChoicePickerNode = import('@a2ui/web_core/v0_9/basic_catalog').ChoicePickerNode;
  export type TextFieldNode = import('@a2ui/web_core/v0_9/basic_catalog').TextFieldNode;
  export type CheckboxNode = import('@a2ui/web_core/v0_9/basic_catalog').CheckBoxNode;
  export type CheckBoxNode = import('@a2ui/web_core/v0_9/basic_catalog').CheckBoxNode;
  export type SliderNode = import('@a2ui/web_core/v0_9/basic_catalog').SliderNode;
  export type DateTimeInputNode = import('@a2ui/web_core/v0_9/basic_catalog').DateTimeInputNode;
  export type TabsNode = import('@a2ui/web_core/v0_9/basic_catalog').TabsNode;
  export type TabItem = import('@a2ui/web_core/v0_9/basic_catalog').TabItem;
  export type ModalNode = import('@a2ui/web_core/v0_9/basic_catalog').ModalNode;
  
  // Link component wasn't in basic_catalog.json but it's used in types.ts.
  // Re-adding it here until a proper migration is mapped.
  export interface LinkProps {
    text: string;
    url: string;
  }
  export type LinkNode = Component<LinkProps>;
  export type Link = LinkNode;
  
  export type CardNode = import('@a2ui/web_core/v0_9/basic_catalog').CardNode;
}

