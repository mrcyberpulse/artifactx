# ArtifactX Desktop (Tauri 2)

This folder scaffolds a Tauri 2 shell that wraps the **same** `frontend/` React build used by
the web app. There is no separate desktop frontend — Tauri loads the built `frontend/dist`
output (or proxies to the Vite dev server during development).

## Status in Part 1

This is a configuration scaffold only. No native build has been executed in this environment.
Building real Windows/macOS/Linux binaries requires platform-specific toolchains that are not
available in this chat/CI context:

- **Windows**: Windows 10/11, Rust, Microsoft C++ Build Tools, WebView2 runtime
- **macOS**: macOS with Xcode Command Line Tools, Rust; code signing requires an Apple Developer
  account and a Developer ID certificate
- **Linux**: Rust, `webkit2gtk`, `libappindicator`, standard build tools (`build-essential` or
  equivalent); AppImage/DEB/RPM packaging each have their own additional tooling

## Prerequisites

1. Install Rust: https://www.rust-lang.org/tools/install
2. Install Tauri CLI: `cargo install tauri-cli --version "^2.0"`
3. Build the frontend once: `cd ../frontend && npm install && npm run build`

## Expected structure (to be completed in Part 4)
