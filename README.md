A simple Python/Flask project for managing and creating SQL Server containers.

This tool is part of my workflow to handle multiple database backups that share the same structure but come from different customers. It allows me to set up several backups by automatically searching for an unused port and spinning up a fresh SQL Server container. This way, I can quickly run the container and simply change the port in my connection settings to switch between customers I’m supporting.
