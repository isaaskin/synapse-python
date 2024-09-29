#!/bin/bash

set -e

export PATH=$PATH:$HOME/.local/bin

poetry install

poetry build
