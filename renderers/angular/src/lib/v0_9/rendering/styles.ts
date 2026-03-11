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

// Ported from web_core v0.8 styles

// --- Shared Constants ---
export const grid = 4;

// --- Types & Utils (Inlined for simplicity) ---

type ColorShade =
  | 0
  | 5
  | 10
  | 15
  | 20
  | 25
  | 30
  | 35
  | 40
  | 50
  | 60
  | 70
  | 80
  | 90
  | 95
  | 98
  | 99
  | 100;

const shades: ColorShade[] = [
  0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 95, 98, 99, 100,
];

type PaletteKeyVals = 'n' | 'nv' | 'p' | 's' | 't' | 'e';

type CreatePalette<Prefix extends PaletteKeyVals> = {
  [Key in `${Prefix}${ColorShade}`]: string;
};

type PaletteKey<Prefix extends PaletteKeyVals> = Array<keyof CreatePalette<Prefix>>;

export function toProp(key: string) {
  if (key.startsWith('nv')) {
    return `--nv-${key.slice(2)}`;
  }

  return `--${key[0]}-${key.slice(1)}`;
}

const getInverseKey = (key: string): string => {
  const match = key.match(/^([a-z]+)(\d+)$/);
  if (!match) return key;
  const [, prefix, shadeStr] = match;
  const shade = parseInt(shadeStr, 10);
  const target = 100 - shade;
  const inverseShade = shades.reduce((prev, curr) =>
    Math.abs(curr - target) < Math.abs(prev - target) ? curr : prev,
  );
  return `${prefix}${inverseShade}`;
};

const keyFactory = <K extends PaletteKeyVals>(prefix: K) => {
  return shades.map((v) => `${prefix}${v}`) as PaletteKey<K>;
};

// --- Styles ---

const opacityBehavior = `
  &:not([disabled]) {
    cursor: pointer;
    opacity: var(--opacity, 0);
    transition: opacity var(--speed, 0.2s) cubic-bezier(0, 0, 0.3, 1);

    &:hover,
    &:focus {
      opacity: 1;
    }
  }`;

export const behavior = `
  ${new Array(21)
    .fill(0)
    .map((_, idx) => {
      return `.behavior-ho-${idx * 5} {
          --opacity: ${idx / 20};
          ${opacityBehavior}
        }`;
    })
    .join('\n')}

  .behavior-o-s {
    overflow: scroll;
  }

  .behavior-o-a {
    overflow: auto;
  }

  .behavior-o-h {
    overflow: hidden;
  }

  .behavior-sw-n {
    scrollbar-width: none;
  }
`;

export const border = `
  ${new Array(25)
    .fill(0)
    .map((_, idx) => {
      return `
        .border-bw-${idx} { border-width: ${idx}px; }
        .border-btw-${idx} { border-top-width: ${idx}px; }
        .border-bbw-${idx} { border-bottom-width: ${idx}px; }
        .border-blw-${idx} { border-left-width: ${idx}px; }
        .border-brw-${idx} { border-right-width: ${idx}px; }

        .border-ow-${idx} { outline-width: ${idx}px; }
        .border-br-${idx} { border-radius: ${idx * grid}px; overflow: hidden;}`;
    })
    .join('\n')}

  .border-br-50pc {
    border-radius: 50%;
  }

  .border-bs-s {
    border-style: solid;
  }
`;

const color = <C extends PaletteKeyVals>(src: PaletteKey<C>) =>
  `
    ${src
      .map((key: string) => {
        const inverseKey = getInverseKey(key);
        return `.color-bc-${key} { border-color: light-dark(var(${toProp(
          key,
        )}), var(${toProp(inverseKey)})); }`;
      })
      .join('\n')}

    ${src
      .map((key: string) => {
        const inverseKey = getInverseKey(key);
        const vals = [
          `.color-bgc-${key} { background-color: light-dark(var(${toProp(
            key,
          )}), var(${toProp(inverseKey)})); }`,
          `.color-bbgc-${key}::backdrop { background-color: light-dark(var(${toProp(
            key,
          )}), var(${toProp(inverseKey)})); }`,
        ];

        for (let o = 0.1; o < 1; o += 0.1) {
          vals.push(`.color-bbgc-${key}_${(o * 100).toFixed(0)}::backdrop {
            background-color: light-dark(oklch(from var(${toProp(
              key,
            )}) l c h / calc(alpha * ${o.toFixed(1)})), oklch(from var(${toProp(
              inverseKey,
            )}) l c h / calc(alpha * ${o.toFixed(1)})) );
          }
        `);
        }

        return vals.join('\n');
      })
      .join('\n')}

  ${src
    .map((key: string) => {
      const inverseKey = getInverseKey(key);
      return `.color-c-${key} { color: light-dark(var(${toProp(
        key,
      )}), var(${toProp(inverseKey)})); }`;
    })
    .join('\n')}
  `;

export const colors = [
  color(keyFactory('p')),
  color(keyFactory('s')),
  color(keyFactory('t')),
  color(keyFactory('n')),
  color(keyFactory('nv')),
  color(keyFactory('e')),
  `
    .color-bgc-transparent {
      background-color: transparent;
    }

    :host {
      color-scheme: var(--color-scheme);
    }
  `,
];

export const icons = `
  .g-icon {
    font-family: "Material Symbols Outlined", "Google Symbols";
    font-weight: normal;
    font-style: normal;
    font-display: optional;
    font-size: 20px;
    width: 1em;
    height: 1em;
    user-select: none;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-feature-settings: "liga";
    -webkit-font-smoothing: antialiased;
    overflow: hidden;

    font-variation-settings: "FILL" 0, "wght" 300, "GRAD" 0, "opsz" 48,
      "ROND" 100;

    &.filled {
      font-variation-settings: "FILL" 1, "wght" 300, "GRAD" 0, "opsz" 48,
        "ROND" 100;
    }

    &.filled-heavy {
      font-variation-settings: "FILL" 1, "wght" 700, "GRAD" 0, "opsz" 48,
        "ROND" 100;
    }
  }
`;

export const layout = `
  :host {
    ${new Array(16)
      .fill(0)
      .map((_, idx) => {
        return `--g-${idx + 1}: ${(idx + 1) * grid}px;`;
      })
      .join('\n')}
  }

  ${new Array(49)
    .fill(0)
    .map((_, index) => {
      const idx = index - 24;
      const lbl = idx < 0 ? `n${Math.abs(idx)}` : idx.toString();
      return `
        .layout-p-${lbl} { --padding: ${idx * grid}px; padding: var(--padding); }
        .layout-pt-${lbl} { padding-top: ${idx * grid}px; }
        .layout-pr-${lbl} { padding-right: ${idx * grid}px; }
        .layout-pb-${lbl} { padding-bottom: ${idx * grid}px; }
        .layout-pl-${lbl} { padding-left: ${idx * grid}px; }

        .layout-m-${lbl} { --margin: ${idx * grid}px; margin: var(--margin); }
        .layout-mt-${lbl} { margin-top: ${idx * grid}px; }
        .layout-mr-${lbl} { margin-right: ${idx * grid}px; }
        .layout-mb-${lbl} { margin-bottom: ${idx * grid}px; }
        .layout-ml-${lbl} { margin-left: ${idx * grid}px; }

        .layout-t-${lbl} { top: ${idx * grid}px; }
        .layout-r-${lbl} { right: ${idx * grid}px; }
        .layout-b-${lbl} { bottom: ${idx * grid}px; }
        .layout-l-${lbl} { left: ${idx * grid}px; }`;
    })
    .join('\n')}

  ${new Array(25)
    .fill(0)
    .map((_, idx) => {
      return `
        .layout-g-${idx} { gap: ${idx * grid}px; }`;
    })
    .join('\n')}

  ${new Array(8)
    .fill(0)
    .map((_, idx) => {
      return `
        .layout-grd-col${idx + 1} { grid-template-columns: ${'1fr '.repeat(idx + 1).trim()}; }`;
    })
    .join('\n')}

  .layout-pos-a {
    position: absolute;
  }

  .layout-pos-rel {
    position: relative;
  }

  .layout-dsp-none {
    display: none;
  }

  .layout-dsp-block {
    display: block;
  }

  .layout-dsp-grid {
    display: grid;
  }

  .layout-dsp-iflex {
    display: inline-flex;
  }

  .layout-dsp-flexvert {
    display: flex;
    flex-direction: column;
  }

  .layout-dsp-flexhor {
    display: flex;
    flex-direction: row;
  }

  .layout-fw-w {
    flex-wrap: wrap;
  }

  .layout-al-fs {
    align-items: start;
  }

  .layout-al-fe {
    align-items: end;
  }

  .layout-al-c {
    align-items: center;
  }

  .layout-as-n {
    align-self: normal;
  }

  .layout-js-c {
    justify-self: center;
  }

  .layout-sp-c {
    justify-content: center;
  }

  .layout-sp-ev {
    justify-content: space-evenly;
  }

  .layout-sp-bt {
    justify-content: space-between;
  }

  .layout-sp-s {
    justify-content: start;
  }

  .layout-sp-e {
    justify-content: end;
  }

  .layout-ji-e {
    justify-items: end;
  }

  .layout-r-none {
    resize: none;
  }

  .layout-fs-c {
    field-sizing: content;
  }

  .layout-fs-n {
    field-sizing: none;
  }

  .layout-flx-0 {
    flex: 0 0 auto;
  }

  .layout-flx-1 {
    flex: 1 0 auto;
  }

  .layout-c-s {
    contain: strict;
  }

  /** Widths **/

  ${new Array(10)
    .fill(0)
    .map((_, idx) => {
      const weight = (idx + 1) * 10;
      return `.layout-w-${weight} { width: ${weight}%; max-width: ${weight}%; }`;
    })
    .join('\n')}

  ${new Array(16)
    .fill(0)
    .map((_, idx) => {
      const weight = idx * grid;
      return `.layout-wp-${idx} { width: ${weight}px; }`;
    })
    .join('\n')}

  /** Heights **/

  ${new Array(10)
    .fill(0)
    .map((_, idx) => {
      const height = (idx + 1) * 10;
      return `.layout-h-${height} { height: ${height}%; }`;
    })
    .join('\n')}

  ${new Array(16)
    .fill(0)
    .map((_, idx) => {
      const height = idx * grid;
      return `.layout-hp-${idx} { height: ${height}px; }`;
    })
    .join('\n')}

  .layout-el-cv {
    & img,
    & video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      margin: 0;
    }
  }

  .layout-ar-sq {
    aspect-ratio: 1 / 1;
  }

  .layout-ex-fb {
    margin: calc(var(--padding) * -1) 0 0 calc(var(--padding) * -1);
    width: calc(100% + var(--padding) * 2);
    height: calc(100% + var(--padding) * 2);
  }
`;

export const opacity = `
  ${new Array(21)
    .fill(0)
    .map((_, idx) => {
      return `.opacity-el-${idx * 5} { opacity: ${idx / 20}; }`;
    })
    .join('\n')}
`;

export const type = `
  :host {
    --default-font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    --default-font-family-mono: "Courier New", Courier, monospace;
  }

  .typography-f-s {
    font-family: var(--font-family, var(--default-font-family));
    font-optical-sizing: auto;
    font-variation-settings: "slnt" 0, "wdth" 100, "GRAD" 0;
  }

  .typography-f-sf {
    font-family: var(--font-family-flex, var(--default-font-family));
    font-optical-sizing: auto;
  }

  .typography-f-c {
    font-family: var(--font-family-mono, var(--default-font-family));
    font-optical-sizing: auto;
    font-variation-settings: "slnt" 0, "wdth" 100, "GRAD" 0;
  }

  .typography-v-r {
    font-variation-settings: "slnt" 0, "wdth" 100, "GRAD" 0, "ROND" 100;
  }

  .typography-ta-s {
    text-align: start;
  }

  .typography-ta-c {
    text-align: center;
  }

  .typography-fs-n {
    font-style: normal;
  }

  .typography-fs-i {
    font-style: italic;
  }

  .typography-sz-ls {
    font-size: 11px;
    line-height: 16px;
  }

  .typography-sz-lm {
    font-size: 12px;
    line-height: 16px;
  }

  .typography-sz-ll {
    font-size: 14px;
    line-height: 20px;
  }

  .typography-sz-bs {
    font-size: 12px;
    line-height: 16px;
  }

  .typography-sz-bm {
    font-size: 14px;
    line-height: 20px;
  }

  .typography-sz-bl {
    font-size: 16px;
    line-height: 24px;
  }

  .typography-sz-ts {
    font-size: 14px;
    line-height: 20px;
  }

  .typography-sz-tm {
    font-size: 16px;
    line-height: 24px;
  }

  .typography-sz-tl {
    font-size: 22px;
    line-height: 28px;
  }

  .typography-sz-hs {
    font-size: 24px;
    line-height: 32px;
  }

  .typography-sz-hm {
    font-size: 28px;
    line-height: 36px;
  }

  .typography-sz-hl {
    font-size: 32px;
    line-height: 40px;
  }

  .typography-sz-ds {
    font-size: 36px;
    line-height: 44px;
  }

  .typography-sz-dm {
    font-size: 45px;
    line-height: 52px;
  }

  .typography-sz-dl {
    font-size: 57px;
    line-height: 64px;
  }

  .typography-ws-p {
    white-space: pre-line;
  }

  .typography-ws-nw {
    white-space: nowrap;
  }

  .typography-td-none {
    text-decoration: none;
  }

  /** Weights **/

  ${new Array(9)
    .fill(0)
    .map((_, idx) => {
      const weight = (idx + 1) * 100;
      return `.typography-w-${weight} { font-weight: ${weight}; }`;
    })
    .join('\n')}
`;

export const structuralStyles: string = [behavior, border, colors, icons, layout, opacity, type]
  .flat(Infinity)
  .join('\n');
