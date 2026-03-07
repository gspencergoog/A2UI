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

import { Action } from '../../v0_8/types/components.js';
import * as Primitives from '../../v0_8/types/primitives.js';

// Base Component Node (Runtime Model Data)
// Note: rendering and wrapper specific frameworks should extend this.
export interface Component<P = Record<string, any>> {
  id: string;
  type: string;
  properties: P;
}

export type AnyComponentNode = Component;

// --- Built-in basic_catalog.json property schemas ---

export interface ButtonProps {
  child?: string;
  action: Action;
  variant?: string; // 'default' | 'primary' | 'borderless'
}
export type ButtonNode = Component<ButtonProps> & {
  child?: string;
};

export interface TextProps {
  text: Primitives.StringValue;
  variant?: string; // 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'caption' | 'body'
  usageHint?: string; // keeping the usageHint inside typescript for now as it's used in older tests
}
export type TextNode = Component<TextProps> & {
  usageHint?: string;
};

export interface ImageProps {
  url: string;
  fit?: string; // 'contain' | 'cover' | 'fill' | 'none' | 'scaleDown'
  variant?: string; // 'icon' | 'avatar' | 'smallFeature' | 'mediumFeature' | 'largeFeature' | 'header'
}
export type ImageNode = Component<ImageProps> & {
  variant?: string;
  fit?: string;
};

export interface IconProps {
  name: string | { path: string };
}
export type IconNode = Component<IconProps>;

export interface AudioProps {
  url: string;
  description?: string;
}
export type AudioPlayerNode = Component<AudioProps> & {
  description?: string;
};

export interface VideoProps {
  url: string;
}
export type VideoNode = Component<VideoProps>;

export interface CardProps {
  child: string;
}
export type CardNode = Component<CardProps> & {
  child: string;
};

export interface DividerProps {
  axis?: string; // 'horizontal' | 'vertical'
}
export type DividerNode = Component<DividerProps>;

export interface RowProps {
  children: string[] | { path: string; componentId: string };
  justify?: string;
  align?: string;
}
export type RowNode = Component<RowProps> & {
  align?: string;
  justify?: string;
};

export interface ColumnProps {
  children: string[] | { path: string; componentId: string };
  justify?: string;
  align?: string;
}
export type ColumnNode = Component<ColumnProps> & {
  align?: string;
  justify?: string;
};

export interface ListProps {
  children: string[] | { path: string; componentId: string };
  direction?: string; // 'vertical' | 'horizontal'
  align?: string;
}
export type ListNode = Component<ListProps> & {
  align?: string;
};

export interface TextFieldProps {
  label: Primitives.StringValue;
  value?: Primitives.StringValue;
  variant?: string; // 'longText' | 'number' | 'shortText' | 'obscured'
  validationRegexp?: string;
}
export type TextFieldNode = Component<TextFieldProps> & {
  variant?: string;
};

export interface CheckBoxProps {
  label: Primitives.StringValue;
  value: Primitives.BooleanValue;
}
export type CheckBoxNode = Component<CheckBoxProps>;

export interface SliderProps {
  label?: Primitives.StringValue;
  value: Primitives.NumberValue;
  min?: number;
  max: number;
}
export type SliderNode = Component<SliderProps>;

export interface DateTimeInputProps {
  label?: Primitives.StringValue;
  value: string;
  enableDate?: boolean;
  enableTime?: boolean;
  min?: string;
  max?: string;
}
export type DateTimeInputNode = Component<DateTimeInputProps>;

export interface ChoicePickerProps {
  label?: Primitives.StringValue;
  value: Primitives.StringValue[];
  variant?: string; // 'multipleSelection' | 'mutuallyExclusive'
  options: { label: string | Primitives.StringValue; value: string }[];
  displayStyle?: string; // 'checkbox' | 'chips'
  filterable?: boolean;
}
export type ChoicePickerNode = Component<ChoicePickerProps>;

export interface ModalProps {
  entryPointChild?: string;
  contentChild?: string;
}
export type ModalNode = Component<ModalProps>;

export interface TabItem {
  title: string | Primitives.StringValue;
  child: string;
}
export interface TabsProps {
  tabs: TabItem[];
}
export type TabsNode = Component<TabsProps> & { tabs: TabItem[] };
