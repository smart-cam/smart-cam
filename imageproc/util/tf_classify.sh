#!/bin/bash

image_file=$1
out_dir=$2

echo "Classifying Image File: ${image_file}"
echo "Output Directory: ${out_dir}"

# Change Directory
#cd ~/tensorflow

# Run Tensorflow
#bazel build tensorflow/examples/label_image:label_image && \
#bazel-bin/tensorflow/examples/label_image/label_image \
#--graph=/tmp/output_graph.pb --labels=/tmp/output_labels.txt \
#--output_layer=final_result \
#--image=$HOME/images/test/frame_1.png

# Create Output File
cat /Users/ssatpati/0-DATASCIENCE/DEV/github/smart-cam/resources/tf.out | \
        grep ^I | awk -F'[\]]' '{print $2}' | awk '{$1=$1};1' > $out_dir/tf.class.out
