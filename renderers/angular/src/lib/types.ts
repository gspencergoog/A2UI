import {
  Action as WebCoreAction,
  FunctionCall as WebCoreFunctionCall,
  A2uiMessage,
} from '@a2ui/web_core/v0_9';
import * as Primitives from '@a2ui/web_core/types/primitives';

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
  export interface Component<P = Record<string, any>> {
    id: string;
    type: string;
    properties: P;
    [key: string]: any; // For flexibility and mixed-in metadata
  }

  export type AnyComponentNode = Component;
  export type CustomNode = AnyComponentNode;

  // --- Button ---
  export interface ButtonProps {
    label?: Primitives.StringValue;
    child?: string;
    action?: Action;
    variant?: string;
  }
  export type ButtonNode = Component<ButtonProps>;
  export type ResolvedButton = ButtonProps;

  // --- Text ---
  export interface TextProps {
    text: Primitives.StringValue;
    variant?: string;
    usageHint?: string;
  }
  export type TextNode = Component<TextProps>;
  export type ResolvedText = TextProps;

  // --- Image ---
  export interface ImageProps {
    url: string;
    altText?: string;
    usageHint?: string;
  }
  export type ImageNode = Component<ImageProps>;
  export type ResolvedImage = ImageProps;

  // --- Icon ---
  export interface IconProps {
    name: string;
    color?: string;
  }
  export type IconNode = Component<IconProps>;
  export type ResolvedIcon = IconProps;

  // --- Audio ---
  export interface AudioProps {
    url: string;
    autoplay?: boolean | string;
    loop?: boolean | string;
  }
  export type AudioPlayerNode = Component<AudioProps>;
  export type ResolvedAudioPlayer = AudioProps;

  // --- Video ---
  export interface VideoProps {
    url: string;
    autoplay?: boolean | string;
    loop?: boolean | string;
    controls?: boolean | string;
  }
  export type VideoNode = Component<VideoProps>;
  export type ResolvedVideo = VideoProps;

  // --- Card ---
  export interface CardProps {
    child?: string;
    children?: string[];
  }
  export type CardNode = Component<CardProps>;
  export type ResolvedCard = CardProps;

  // --- Divider ---
  export interface DividerProps {}
  export type DividerNode = Component<DividerProps>;
  export type ResolvedDivider = DividerProps;

  // --- Row ---
  export interface RowProps {
    children: string[];
    alignment?: string;
    justify?: string;
    align?: string;
    distribution?: string;
    gap?: string;
  }
  export type RowNode = Component<RowProps>;
  export type ResolvedRow = RowProps;

  // --- Column ---
  export interface ColumnProps {
    children: string[];
    alignment?: string;
    justify?: string;
    align?: string;
    distribution?: string;
    gap?: string;
  }
  export type ColumnNode = Component<ColumnProps>;
  export type ResolvedColumn = ColumnProps;

  // --- List ---
  export interface ListProps {
    children: string[] | { path: string; componentId: string };
    direction?: string;
  }
  export type ListNode = Component<ListProps>;
  export type ResolvedList = ListProps;

  // --- TextField ---
  export interface TextFieldProps {
    label?: Primitives.StringValue;
    value?: Primitives.StringValue;
    placeholder?: Primitives.StringValue;
    action?: Action;
    type?: string; // Input type (text, password, etc)
  }
  export type TextFieldNode = Component<TextFieldProps>;
  export type ResolvedTextField = TextFieldProps;

  // --- CheckBox ---
  export interface CheckBoxProps {
    label?: string;
    value?: boolean | string;
    action?: Action;
  }
  export type CheckBoxNode = Component<CheckBoxProps>;
  export type CheckboxNode = CheckBoxNode; // Alias for inconsistent naming
  export type ResolvedCheckBox = CheckBoxProps;

  // --- Slider ---
  export interface SliderProps {
    value?: number | string;
    min?: number | string;
    max?: number | string;
    step?: number | string;
    label?: Primitives.StringValue;
    action?: Action;
  }
  export type SliderNode = Component<SliderProps>;
  export type ResolvedSlider = SliderProps;

  // --- DateTimeInput ---
  export interface DateTimeInputProps {
    label?: Primitives.StringValue;
    value?: string;
    action?: Action;
    enableDate?: boolean;
    enableTime?: boolean;
    type?: string;
  }
  export type DateTimeInputNode = Component<DateTimeInputProps>;
  export type ResolvedDateTimeInput = DateTimeInputProps;

  // --- ChoicePicker ---
  export interface ChoicePickerProps {
    label?: Primitives.StringValue;
    value?: string;
    options: string | { label: string; value: string }[] | { path: string };
    action?: Action;
  }
  export type ChoicePickerNode = Component<ChoicePickerProps>;
  export type ResolvedChoicePicker = ChoicePickerProps;
  // MultipleChoiceNode alias if needed
  export type MultipleChoiceNode = ChoicePickerNode;

  // --- Modal ---
  export interface ModalProps {
    entryPointChild: string;
    contentChild: string;
  }
  export type ModalNode = Component<ModalProps>;
  export type ResolvedModal = ModalProps;

  // --- Tabs ---
  export interface TabItem {
    title: string;
    child: string;
  }
  export interface TabsProps {
    tabs: TabItem[];
  }
  export type TabsNode = Component<TabsProps>;
  export type ResolvedTabs = TabsProps;
  export type ResolvedTabItem = TabItem;

  // --- Link ---
  export interface LinkProps {
    text: string;
    url: string;
  }
  export type LinkNode = Component<LinkProps>;
  export type ResolvedLink = LinkProps;

  // --- Surface ---
  export interface SurfaceProps {
    content: string;
  }
  // Surface might not be a component in the same way?

  export type ServerToClientMessage = A2uiMessage;

  export interface Theme {
    components?: any;
    additionalStyles?: any;
    [key: string]: any;
  }

  // Aliases for backward compatibility
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
  export type Link = LinkNode;
  export type ChoicePicker = ChoicePickerNode;
}
