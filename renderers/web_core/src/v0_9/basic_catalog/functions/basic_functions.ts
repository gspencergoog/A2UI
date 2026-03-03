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
  EvaluationContext,
  FunctionImplementation,
} from "../expressions/expression_evaluator.js";

export const BASIC_FUNCTIONS: Record<string, FunctionImplementation> = {
  // Arithmetic
  add: (args) => (Number(args["a"]) || 0) + (Number(args["b"]) || 0),
  subtract: (args) => (Number(args["a"]) || 0) - (Number(args["b"]) || 0),
  multiply: (args) => (Number(args["a"]) || 0) * (Number(args["b"]) || 0),
  divide: (args) => (Number(args["a"]) || 0) / (Number(args["b"]) || 1),

  // Comparison
  equals: (args) => args["a"] === args["b"],
  not_equals: (args) => args["a"] !== args["b"],
  greater_than: (args) => (Number(args["a"]) || 0) > (Number(args["b"]) || 0),
  less_than: (args) => (Number(args["a"]) || 0) < (Number(args["b"]) || 0),

  // Logical
  and: (args) => {
    if (Array.isArray(args["values"])) {
      return args["values"].every((v: unknown) => !!v);
    }
    return !!(args["a"] && args["b"]); // Fallback
  },
  or: (args) => {
    if (Array.isArray(args["values"])) {
      return args["values"].some((v: unknown) => !!v);
    }
    return !!(args["a"] || args["b"]); // Fallback
  },
  not: (args) => !args["value"],

  // String
  contains: (args) =>
    String(args["string"] || "").includes(String(args["substring"] || "")),
  starts_with: (args) =>
    String(args["string"] || "").startsWith(String(args["prefix"] || "")),
  ends_with: (args) =>
    String(args["string"] || "").endsWith(String(args["suffix"] || "")),

  // Validation
  required: (args) => {
    const val = args["value"];
    if (val === null || val === undefined) return false;
    if (typeof val === "string" && val === "") return false;
    if (Array.isArray(val) && val.length === 0) return false;
    return true;
  },

  regex: (args) => {
    const val = String(args["value"] || "");
    const pattern = String(args["pattern"] || "");
    try {
      return new RegExp(pattern).test(val);
    } catch (e) {
      console.warn("Invalid regex pattern:", pattern);
      return false;
    }
  },

  length: (args) => {
    const val = args["value"];
    let len = 0;
    if (typeof val === "string" || Array.isArray(val)) {
      len = val.length;
    }
    const min = Number(args["min"]);
    const max = Number(args["max"]);
    if (!isNaN(min) && len < min) return false;
    if (!isNaN(max) && len > max) return false;
    return true;
  },

  numeric: (args) => {
    const val = Number(args["value"]);
    if (isNaN(val)) return false;
    const min = Number(args["min"]);
    const max = Number(args["max"]);
    if (!isNaN(min) && val < min) return false;
    if (!isNaN(max) && val > max) return false;
    return true;
  },

  email: (args) => {
    const val = String(args["value"] || "");
    // Simple email regex
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
  },

  // Formatting
  formatString: (args, context: EvaluationContext) => {
    const template = String(args["value"] || "");
    if (context.parser) {
      return context.parser.parse(template);
    }
    throw new Error(
      "ExpressionParser is required for formatString but was not provided in the evaluation context.",
    );
  },

  formatNumber: (args) => {
    const val = Number(args["value"]);
    if (isNaN(val)) return "";
    const decimals =
      args["decimals"] !== undefined ? Number(args["decimals"]) : undefined;
    const grouping = args["grouping"] !== false; // Default true
    return new Intl.NumberFormat("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
      useGrouping: grouping,
    }).format(val);
  },

  formatCurrency: (args) => {
    const val = Number(args["value"]);
    if (isNaN(val)) return "";
    const currency = String(args["currency"] || "USD");
    const decimals =
      args["decimals"] !== undefined ? Number(args["decimals"]) : undefined;
    const grouping = args["grouping"] !== false;
    try {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency,
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
        useGrouping: grouping,
      }).format(val);
    } catch (e) {
      return val.toFixed(decimals || 2);
    }
  },

  formatDate: (args) => {
    const val = args["value"];
    if (!val) return "";
    const date = new Date(val as string | number | Date);
    if (isNaN(date.getTime())) return "";

    const locale = String(args["locale"] || "en-US");
    const options = args["options"] as Intl.DateTimeFormatOptions;

    try {
      if (options) {
        return new Intl.DateTimeFormat(locale, options).format(date);
      }

      // Fallback for simple format strings if we want to support them (optional)
      // For now, we'll default to standard date string or ISO if requested
      const format = String(args["format"] || "");
      if (format === "ISO") return date.toISOString();

      return new Intl.DateTimeFormat(locale).format(date);
    } catch (e) {
      console.warn("Error formatting date:", e);
      return date.toISOString();
    }
  },

  pluralize: (args) => {
    const val = Number(args["value"]) || 0;
    const rule = new Intl.PluralRules("en-US").select(val);
    // args: zero, one, two, few, many, other
    return String(args[rule] || args["other"] || "");
  },
};
