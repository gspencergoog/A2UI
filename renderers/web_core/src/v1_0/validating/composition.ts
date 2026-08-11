/**
 * @fileoverview Component Composition Rules and Validation for A2UI v1.0.
 *
 * Enforces surface root component rules ("Surface" as root) and container
 * parent/child component relationship constraints.
 */

import {CatalogDefinition, ComponentDefinition} from '../catalog/catalog-definition.js';

export interface ComponentInstance {
  id: string;
  type: string;
  parentId?: string;
  children?: string[];
}

export interface CompositionValidationError {
  componentId: string;
  message: string;
  rule: 'surface_root' | 'allowed_parents' | 'allowed_children';
}

/**
 * Validates surface composition rules across all components in a surface.
 */
export function validateComposition(
  components: ComponentInstance[],
  rootComponentId: string,
  catalog?: CatalogDefinition,
): CompositionValidationError[] {
  const errors: CompositionValidationError[] = [];
  const compMap = new Map<string, ComponentInstance>();
  components.forEach(c => compMap.set(c.id, c));

  // 1. Surface Root Component Rule
  const rootComp = compMap.get(rootComponentId);
  if (!rootComp) {
    errors.push({
      componentId: rootComponentId,
      message: `Root component '${rootComponentId}' not found in surface components.`,
      rule: 'surface_root',
    });
  } else if (rootComp.type !== 'Surface') {
    errors.push({
      componentId: rootComponentId,
      message: `Surface root component must be of type 'Surface', got '${rootComp.type}'.`,
      rule: 'surface_root',
    });
  }

  // If catalog is provided, validate parent/child restrictions
  if (catalog && catalog.components) {
    const catalogComps = catalog.components;

    components.forEach(comp => {
      const def: ComponentDefinition | undefined = catalogComps[comp.type];
      if (!def) return;

      // 2. Allowed Parents Validation
      if (comp.parentId) {
        const parentComp = compMap.get(comp.parentId);
        if (!parentComp) {
          errors.push({
            componentId: comp.id,
            message: `Component '${comp.id}' references parent '${comp.parentId}' which does not exist.`,
            rule: 'allowed_parents',
          });
        } else if (def.allowedParents !== undefined) {
          if (!def.allowedParents.includes(parentComp.type)) {
            errors.push({
              componentId: comp.id,
              message: `Component '${comp.id}' of type '${comp.type}' is not allowed under parent '${parentComp.id}' of type '${parentComp.type}'. Allowed parents: [${def.allowedParents.join(', ')}].`,
              rule: 'allowed_parents',
            });
          }
        }
      }

      // 3. Allowed Children Validation
      if (comp.children && comp.children.length > 0 && def.allowedChildren !== undefined) {
        comp.children.forEach(childId => {
          const childComp = compMap.get(childId);
          if (!childComp) {
            errors.push({
              componentId: comp.id,
              message: `Container '${comp.id}' references child '${childId}' which does not exist.`,
              rule: 'allowed_children',
            });
          } else if (!def.allowedChildren!.includes(childComp.type)) {
            errors.push({
              componentId: comp.id,
              message: `Container '${comp.id}' of type '${comp.type}' does not allow child '${childComp.id}' of type '${childComp.type}'. Allowed children: [${def.allowedChildren!.join(', ')}].`,
              rule: 'allowed_children',
            });
          }
        });
      }
    });
  }

  return errors;
}
