#!/bin/bash

image_file=$1
out_file=$2

echo "Classifying Image File: ${image_file}"
echo "Output File: ${out_file}"

# Change Directory
cd ~/tensorflow

# Run Tensorflow & dump to a temp file
bazel-bin/tensorflow/examples/label_image/label_image \
--graph=/tmp/output_graph.pb --labels=/tmp/output_labels.txt \
--output_layer=final_result \
--image=${image_file} > ${out_file}_tmp 2>&1

# Create Output File
cat ${out_file}_tmp | grep ^I | awk -F'[\]]' '{print $2}' | awk '{$1=$1};1' > $out_file

# Remove Temp File
rm ${out_file}_tmp
