# Petrodactal Monitor

A Pterodactyl game-server monitoring dashboard.

## Version 2 rewrite

The new rewrite is being developed in the `v2/` directory on the `rewrite-development` branch. The original application remains available separately while v2 is built and tested.

**For v2 installation instructions**, see [v2/README.md](v2/README.md).

An Ubuntu installer is available at [v2/install-ubuntu.sh](v2/install-ubuntu.sh). It prepares the initial Django application, PostgreSQL database, Python environment, Gunicorn service, and Nginx configuration.

> **Development status:** v2 is not yet production-ready and has not yet been installed or verified on the project owner's VPS. The installer is an initial development deployment helper, not the planned in-app software updater. Review the installation warnings in the v2 README before running it.

## Original application

The original application and its existing installation files are retained in the repository for reference. The root-level legacy installer applies to the original application, not the v2 rewrite.
