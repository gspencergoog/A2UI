import preset from '../../eslint.preset.mjs';

export default [
  ...preset,
  { ignores: ['a2ui_explorer/**'] }
];
