
import time
import tensorflow as tf
import base64

model_dir = "C:/Users/Daly/Desktop/inception-face-shape-classifier-master/model"

model_path = model_dir + "/retrained_graph.pb"
labels_path = model_dir + "/retrained_labels.txt"

def base64_to_jpeg(imgstring):
        img_data = base64.b64decode(imgstring)
        return img_data

class face():        
    
    def classify_image(imgbase64):
        image_data =  base64_to_jpeg(imgbase64)
        # Read in the image_data
        time_start = time.monotonic()
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth=True
        sess = tf.compat.v1.Session(config=config)
    
        #image_data = tf.compat.v1.gfile.FastGFile(image_path, 'rb').read()
    
        # Loads label file, strips off carriage return
        label_lines = [line.rstrip() for line 
                           in tf.io.gfile.GFile(labels_path)]
    
        # Unpersists graph from file
        with tf.compat.v1.gfile.FastGFile(model_path, 'rb') as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')
    
        with tf.compat.v1.Session() as sess:
            # Feed the image_data as input to the graph and get first prediction
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            
            predictions = sess.run(softmax_tensor, \
                     {'DecodeJpeg/contents:0': image_data})
        
            # Sort to show labels of first prediction in order of confidence
            top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
    
            output_label = ""
            
            for node_id in top_k:
                human_string = label_lines[node_id]
                score = predictions[0][node_id]
                output_label = output_label + human_string + "({0:.4f})".format(score) + " "
                #print('%s (score = %.5f)' % (human_string, score))
            #print(output_label)
            output_label = output_label + " Runtime: " + "{0:.2f}".format(time.monotonic()-time_start) + "s"
        
        #OUTPUT_LABEL is square(0.5497) round(0.2785) oval(0.1059) heart(0.0517) oblong(0.0142)
        sess.close()
        return label_lines[top_k[0]]