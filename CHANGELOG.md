# Changelog

All notable changes to this project will be documented in this file.

## [0.0.4] - 2026-01-21


### Added
- **Feature**: Added publishing of IODevice information under `PREFIX/heatareas/NOM/iodevice/`.
- **Feature**: Added publishing of Global Device information under `PREFIX/device/`.

### Changed
- **Dependencies**: Upgraded `pyrehau-neasmart` to version `0.0.8`.
- **CI/CD**: Restricted Docker image push to only occur on version tags (e.g. `v…`).
- **MQTT**: Changed topic structure to include `/heatareas/` prefix (e.g. `prefix/heatareas/room/temp`).
- **Refactor**: Improved data retrieval by iterating over IODevices to fetch associated HeatAreas.

## [0.0.3] - 2026-01-21

### Added
- **Development Environment**: Added `docker-compose.dev.yml` to run Mosquitto and the application locally.
- **CI/CD**: Added GitHub Actions workflow (`docker-publish.yml`) to build and push Docker images to Docker Hub and create GitHub Releases on tag push.
- **Configuration**: Added support for `.env` file to override environment variables (e.g. `REHAU_HOST`).
- **Configuration**: Added `mosquitto/config/mosquitto.conf` for local broker development.

### Changed
- **Dependencies**: Updated `requirements.txt` with pinned versions compatible with Python 3.14.
- **Documentation**: Updated `README.md` with comprehensive instructions for development, configuration, and deployment.
- **Code Refactoring (`main.py`)**:
    - Fixed critical `NameError` (missing `self`).
    - Fixed Regex logic and `SyntaxWarning`.
    - Simplified threading model (removed redundant usage).
    - Hardened main loop and error handling.
