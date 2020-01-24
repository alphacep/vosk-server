#!/bin/bash

set -e
set -x

declare -A TAGS_TO_BASE_IMAGES=( \
    ["alphacep/kaldi-vosk-server:latest"]="debian:buster" \
    ["alphacep/kaldi-vosk-server-rpi:latest"]="balenalib/armv7hf-debian:buster" \
)

cd $(dirname "$0")

build_image() {
    tag="$1"
    base_image="$2"
    docker_context="$3"
    echo "Building image ${tag} based on ${base_image} in ${docker_context}"
    docker build --build-arg "BASE_IMAGE=${base_image}" --tag "${tag}" "${docker_context}"
}

for vosk_server_tag in "${!TAGS_TO_BASE_IMAGES[@]}"; do
    base_image="${TAGS_TO_BASE_IMAGES[$vosk_server_tag]}"
    build_image ${vosk_server_tag} ${base_image} .

    for lang_dockerfile in langs/*/Dockerfile; do
        lang_dir=$(dirname ${lang_dockerfile})
        lang=$(basename ${lang_dir})
        lang_tag="${vosk_server_tag/vosk-server/$lang}"
        build_image ${lang_tag} ${vosk_server_tag} ${lang_dir}
    done
done
