#!/bin/bash

# Automated Git Flow setup for the Architecture-Bot project
set -e

if ! command -v git-flow >/dev/null 2>&1; then
  echo "git-flow not found. Installing..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y git-flow
  elif command -v brew >/dev/null 2>&1; then
    brew install git-flow-avh
  else
    echo "Cannot install git-flow automatically." >&2
    exit 1
  fi
fi

git flow init -d

# configure useful aliases
for pair in \
  "ffs=flow feature start" \
  "fff=flow feature finish" \
  "frs=flow release start" \
  "frf=flow release finish" \
  "fhs=flow hotfix start" \
  "fhf=flow hotfix finish"; do
  git config --global alias."${pair%%=*}" "${pair#*=}"
done

echo "Git Flow initialized with default settings."
