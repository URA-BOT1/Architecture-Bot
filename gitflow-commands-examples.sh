#!/bin/bash
# Example Git Flow commands for common actions.
# Execute this script to display a quick reference.

cat <<'CMDS'
# Initialize Git Flow with default settings
git flow init -d

# Start a new feature named "my-feature"
git flow feature start my-feature

# Finish the feature
git flow feature finish my-feature

# Start a release "1.0.0"
git flow release start 1.0.0

# Finish the release
git flow release finish 1.0.0

# Start a hotfix "hotfix-1.0.1"
git flow hotfix start hotfix-1.0.1

# Finish the hotfix
git flow hotfix finish hotfix-1.0.1

# View active branches
git flow feature
git flow release
git flow hotfix
CMDS

