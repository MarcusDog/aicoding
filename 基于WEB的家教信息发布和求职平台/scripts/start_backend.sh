#!/bin/zsh
set -e

export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export PATH="/opt/homebrew/opt/openjdk@17/bin:/opt/homebrew/bin:$PATH"

"$(dirname "$0")/sync_frontend.sh"

cd "$(dirname "$0")/../backend"
mvn spring-boot:run
