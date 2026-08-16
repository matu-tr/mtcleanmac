# MTCleanMac

Menu bar (status bar) app for macOS that cleans caches, logs, Xcode
derived data, and local Time Machine snapshots with a single click.

Licensed under [AGPL-3.0](LICENSE).

## Run from source

```bash
pip3 install -r requirements.txt
python3 menu_bar_app.py
```

## Build a standalone .app locally

```bash
pip3 install -r requirements.txt py2app
python3 setup.py py2app
```

The bundle is written to `dist/MTCleanMac.app`.

## Release process (GitHub Actions)

Releases are built automatically by [.github/workflows/release.yml](.github/workflows/release.yml)
on a macOS runner and published as a GitHub Release with the `.app` zipped up.
The build is ad-hoc code-signed (no Apple Developer account required); on
first launch macOS Gatekeeper will require right-click > Open once.

To cut a release:

1. Bump the version in [VERSION](VERSION) (semantic versioning) and commit it.
2. Tag the commit to match, prefixed with `v`, and push the tag:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. GitHub Actions builds `MTCleanMac.app`, zips it, and attaches it to a new
   Release for that tag. The workflow fails if the tag doesn't match `VERSION`.

You can also trigger a one-off test build without tagging via the
"Run workflow" button on the Actions tab (`workflow_dispatch`); it uploads
the build as a workflow artifact instead of a Release.

## Autostart at login

Add the built `MTCleanMac.app` to System Settings > General > Login Items.
