import subprocess

THRESHOLD = 0.6 # minimum value for successful classification
COMMAND = ['/home/ubuntu/tensorflow/bazel-bin/tensorflow/examples/label_image/label_image', '--graph=/tmp/output_graph2.pb', '--labels=/tmp/output_labels2.txt', '--output_layer=final_result', '--image=']

def classifyImage(filename):
    class_command = COMMAND
    class_command[-1] += filename
    process = subprocess.Popen(class_command, stderr=subprocess.PIPE)
    out, err = process.communicate()
    err_parse = err.split('\n')
    results = dict()

    # load results into dict
    for line in err_parse:
        if len(line) > 0 and line[0] == 'I':
            # assume lines look like this:
            # I tensorflow/examples/label_image/main.cc:207] indoor (2): 0.687276
            output = line.split()
            # score is the key, value is the class
            results[float(output[-1])] = output[2]

    key = max(results.keys())

    # only return value if model confidence meets threshold
    if key >= THRESHOLD:
        return (results[key], key)
    else:
        return None

if __name__ == "__main__":
    filename = "/home/ubuntu/test5.jpg"
    result = classifyImage(filename)
    if result:
        print result
