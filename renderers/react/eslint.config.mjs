import preset from "../../eslint.preset.mjs";

export default [
  ...preset,
  { ignores: ["visual-parity/**"] }
];
