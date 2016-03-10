#!/bin/bash

IMAGE_ID=$1

if [ -z "$IMAGE_ID" ]; then
    echo "Must pass in image id as first arg."
    exit 1
fi

cat > terraform.tfvars <<EOF
config.image_id = "$IMAGE_ID"
EOF
