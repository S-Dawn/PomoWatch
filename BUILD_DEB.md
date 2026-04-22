# Build a .deb package for PomoWatch

This guide is for maintainers who want to create a Debian package file.

## Build with VS Code tasks (recommended)

This repository already includes packaging tasks in `.vscode/tasks.json`.

1. Open Command Palette and run `Tasks: Run Task`.
2. Select `Package: Full .deb workflow`.
3. After build completes, run `Install: local .deb from dist` to test local installation.

Available packaging tasks:

- `Package: Install build dependencies`
- `Package: Build .deb`
- `Package: Move .deb to dist`
- `Package: Clean generated artifacts`
- `Package: Full .deb workflow`
- `Install: local .deb from dist`

## Build from terminal (manual alternative)

## 1) Install build tools

Run on Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y build-essential devscripts debhelper dh-python dpkg-dev
```

## 2) Build package

From the project root:

```bash
dpkg-buildpackage -us -uc
```

The build output files are created in the parent directory.

## 3) Move only the needed file

The only file end users need is:

pomowatch_VERSION_all.deb

You can move it into a local dist folder:

```bash
mkdir -p dist
mv ../pomowatch_*_all.deb dist/
```

## 4) Clean generated build artifacts

Generated files like .buildinfo, .changes, .dsc, and source tarball are not required for end-user local installation.

Remove them from parent directory:

```bash
find .. -maxdepth 1 -type f \( -name 'pomowatch_*.buildinfo' -o -name 'pomowatch_*.changes' -o -name 'pomowatch_*.dsc' -o -name 'pomowatch_*.tar.xz' -o -name 'pomowatch_*_all.deb' \) -delete
```

Remove debhelper generated files from debian/:

```bash
rm -rf debian/.debhelper debian/pomowatch debian/debhelper-build-stamp debian/files
find debian -maxdepth 1 -type f \( -name '*.debhelper' -o -name '*.substvars' \) -delete
```

## 5) Publish for users

Recommended: upload the .deb from dist/ to GitHub Releases (as a release asset), not to source tree commits.

Users can then download and install with apt:

```bash
wget https://github.com/S-Dawn/PomoWatch/releases/download/<tag>/pomowatch_<version>_all.deb
sudo apt install ./pomowatch_<version>_all.deb
```

## Notes

- If your package version changes, update debian/changelog before rebuilding.
- Audio chime is optional in the app package if python sound libraries are unavailable in apt.
