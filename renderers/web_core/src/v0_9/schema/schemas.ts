import {
  ComponentIdSchema,
  ChildListSchema,
  DataBindingSchema,
  DynamicValueSchema,
  DynamicStringSchema,
  DynamicNumberSchema,
  DynamicBooleanSchema,
  DynamicStringListSchema,
  FunctionCallSchema,
  LogicExpressionSchema,
  CheckRuleSchema,
  CheckableSchema,
  ActionSchema,
  AccessibilityAttributesSchema,
  AnyComponentSchema,
} from "./common-types.js";
import {
  CreateSurfaceMessageSchema,
  UpdateComponentsMessageSchema,
  UpdateDataModelMessageSchema,
  DeleteSurfaceMessageSchema,
} from "./server-to-client.js";
import {
  A2uiClientActionSchema,
  A2uiValidationErrorSchema,
  A2uiGenericErrorSchema,
  A2uiClientMessageSchema,
  A2uiClientDataModelSchema,
} from "./client-to-server.js";
import { BASIC_COMPONENTS } from "../basic_catalog/components/basic_components.js";

export const CommonSchemas = {
  ComponentId: ComponentIdSchema,
  ChildList: ChildListSchema,
  DataBinding: DataBindingSchema,
  DynamicValue: DynamicValueSchema,
  DynamicString: DynamicStringSchema,
  DynamicNumber: DynamicNumberSchema,
  DynamicBoolean: DynamicBooleanSchema,
  DynamicStringList: DynamicStringListSchema,
  FunctionCall: FunctionCallSchema,
  LogicExpression: LogicExpressionSchema,
  CheckRule: CheckRuleSchema,
  Checkable: CheckableSchema,
  Action: ActionSchema,
  AccessibilityAttributes: AccessibilityAttributesSchema,
  AnyComponent: AnyComponentSchema,
};

export const ServerToClientMessageSchemas = {
  CreateSurfaceMessage: CreateSurfaceMessageSchema,
  UpdateComponentsMessage: UpdateComponentsMessageSchema,
  UpdateDataModelMessage: UpdateDataModelMessageSchema,
  DeleteSurfaceMessage: DeleteSurfaceMessageSchema,
};

export const ClientToServerMessageSchemas = {
  A2uiClientAction: A2uiClientActionSchema,
  A2uiValidationError: A2uiValidationErrorSchema,
  A2uiGenericError: A2uiGenericErrorSchema,
  A2uiClientMessage: A2uiClientMessageSchema,
  A2uiClientDataModel: A2uiClientDataModelSchema,
};

export { BASIC_COMPONENTS };
