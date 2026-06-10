import preset from '../../../eslint.preset.mjs';

export default [
  ...preset,
  {
    languageOptions: {
      parserOptions: {
        project: false,
      },
    },
  },
];
