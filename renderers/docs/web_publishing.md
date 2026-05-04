# Publishing Guide for A2UI Web Packages

This guide is for project maintainers. It details the publishing process to the npm registry for all web-related packages in this repository.

## Automated Release Workflow (Recommended)

The following scripts in `renderers/scripts/` automate the versioning, building, testing, and publishing of packages. These should generally be run from the `main` branch after a PR has been merged.

### Pre-requirement: Artifact registry configuration

_(Note: Only Googlers will be able to do this. This is a one-time setup.)_

Add the following line to your `~/.npmrc` file:

```
//us-npm.pkg.dev/oss-exit-gate-prod/a2ui--npm/:_authToken=<auth_token>
```

The `<auth_token>` field gets populated by the `google-artifactregistry-auth`
command on "Step 2" later.

### 1. Increment Versions (Local)

To increment a package version and automatically sync all internal dependents (updating their `package-lock.json` files). This should be done in a PR:

```sh
# Automatically increment patch version (e.g. 0.9.5 -> 0.9.6)
renderers/scripts/increment_version.mjs web_core

# Set a specific version (e.g. including pre-releases)
renderers/scripts/increment_version.mjs lit 0.9.2-beta.1
```

This script will:
- Update the `package.json` of the target package.
- Scan the entire mono-repo for internal dependents (via `file:` links).
- Run `npm install` in those dependents to update their lockfiles.

### 2. Publish to Staging (Artifact Registry)

Once versions are updated and merged into `main`, use the `publish_npm` script to build, test, and upload the packages to Google's internal Artifact Registry.

```sh
# Publish multiple packages (they will be sorted automatically by dependency)
./renderers/scripts/publish_npm.mjs --packages=lit,web_core
```

This script will:
- Run `npx google-artifactregistry-auth` to authenticate.
- Sort packages topologically (e.g., publishing `web_core` before `lit`).
- Verify that if a renderer is being published, `web_core` is also included (use `--force` to skip).
- Run pre-flight checks against existing `npmjs` versions and prompt for confirmation.
- For each package: `npm install` -> `npm test` -> `npm run publish:package`.

**Advanced Flags for publish_npm.mjs:**
- `--force`: Skips the `web_core` inclusion warning.
- `--yes`: Bypasses the manual user confirmation prompt (useful for CI).
- `--dry-run`: Simulates the process, printing the commands it *would* execute without actually running them.
- `--skip-tests`: Skips the `npm run test` phase before publishing.
- `--test-only`: Runs the full build and test suite in topological order, but skips the final `npm run publish:package` step. Useful for verifying that packages build and tests pass before performing a real release.

### 3. Upload Manifest

Finally, trigger the public release to npmjs.com by uploading a manifest file:

```sh
./renderers/scripts/upload_manifest.mjs
```

This generates a `manifest.json` with the current versions of all renderer packages and uploads it to GCS to trigger the internal release infrastructure. You should receive an email from exit-gate noting that publishing has commenced.

#### Manual alternative

You can also do this step manually, if you are authenticated with `gcloud` with a corporate Google account in the correct groups:

1. Create a new manifest.json file with these contents:
   ```json
   {
     "publish_all": true
   }
   ```

2. Upload the file

   ```sh
   gcloud storage cp manifest.json gs://oss-exit-gate-prod-projects-bucket/a2ui/npm/manifests/manifest.json
   ```

---

## Internal Release Process

The internal release infrastructure monitors the GCS bucket for new manifests. Once a manifest is uploaded, it triggers a series of checks and then publishes the specified versions to the public npm registry.

Export your token in your terminal:

```sh
export NPM_TOKEN="npm_YourSecretTokenHere"
```

### 🏢 Internal Artifact Registry Setup (Exit Gate) - For Yarn Modern

If you need to publish to the internal Google Artifact Registry (e.g., for Exit Gate validation), you can configure the registry and authentication for the `@a2ui` scope together in your `.yarnrc.yml` file.

Add the following temporarily for publishing (do not commit as it may break CI due to missing auth in automated runs):

```yaml
npmScopes:
  a2ui:
    npmRegistryServer: "https://us-npm.pkg.dev/oss-exit-gate-prod/a2ui--npm/"
    npmAlwaysAuth: true
    npmAuthToken: "${NPM_TOKEN:-}"
```

1. Ensure your local `.npmrc` in the package directory is correctly configured if you are debugging, but the automated scripts handle authentication via `google-artifactregistry-auth`.
2. If you need to manually overwrite or create an `.npmrc` for local testing:
   ```sh
   echo "//registry.npmjs.org/:_authToken=\${NPM_TOKEN}" > .npmrc
   ```

## About the `publish:package` command

Because these are scoped packages (`@a2ui/`), they require the `--access public` flag to be published to the public registry. The `publish:package` script handles this automatically, as well as replacing the path dependencies with package dependencies.

```sh
yarn publish:package
```

*Note: This command runs the build, prepares the `dist/` directory, and then executes `yarn npm publish --access public`.*

---

### How It Works

### Pre-flight Checks

1. Ensure your working tree is clean and you are on the correct branch (e.g., `main`).
2. Update the `version` in `renderers/web_core/package.json`.
3. Verify all tests pass:
   ```sh
   yarn workspace @a2ui/web_core run test
   ```

### Publish to NPM

Run the automated publish script from the repository root:

```sh
yarn workspace @a2ui/web_core run publish:package
```

_Note: The script automatically builds the project, runs `prepare-publish.mjs` to copy artifacts to the `dist/` directory, and publishes from there as public access._

**What exactly gets published?**
Only the `dist/` directory contents are uploaded. This is controlled by the `"files"` array in `package.json` and the `prepare-publish.mjs` script.

---

## 📦 2. Publishing `@a2ui/lit`, `@a2ui/angular`, and `@a2ui/markdown-it`

These packages depend on `@a2ui/web_core` via workspace paths for development. They must be published from their generated `dist/` folders. We use specialized scripts to automatically rewrite their `package.json` with the correct `@a2ui/web_core` npm version before publishing.

### Pre-flight Checks

1. Ensure `@a2ui/web_core` is already published (or its version string is correctly updated) since these packages will read that version number.
2. Update the `version` in the package you want to publish (e.g., `renderers/lit/package.json`).
3. Verify all tests pass:
   ```sh
   yarn workspace @a2ui/lit run test
   yarn workspace @a2ui/angular run test
   ```

### Publish to NPM

Run the automated publish script from the repository root:

**For Lit:**

```sh
yarn workspace @a2ui/lit run publish:package
```

**For Angular:**

```sh
yarn workspace @a2ui/angular run publish:package
```

**For Markdown-it:**

```sh
yarn workspace @a2ui/markdown-it run publish:package
```

### How It Works (Explanations)

**What happens during `publish:package`?**
Before publishing, the script runs the necessary `build` command which processes the code. For Lit and Markdown-it, `prepare-publish.mjs` runs, and for Angular, `postprocess-build.mjs` runs. These scripts:

1. Copy `package.json`, `README.md`, and `LICENSE` to the `dist/` folder.
2. Read the `version` from `@a2ui/web_core`.
3. Update the `workspace:` dependency in the `dist/package.json` to the actual core version (e.g., `^0.8.0`).
4. Adjust exports and paths to be relative to `dist/`.
5. Remove any build scripts (`prepublishOnly`, `scripts`) so they don't interfere with the publish process.

The script then `cd`s to the `dist/` directory and runs `yarn npm publish` to upload only the contents of the `dist/` directory to the npm registry.

---

## 🔖 Post-Publish

1. Tag the release (replace with actual version):
   ```sh
   git tag v0.8.0
   ```
2. Push the tag:
   ```sh
   git push origin v0.8.0
   ```
3. Create a GitHub Release mapping to the new tag.
