import pickle
from keras.models import load_model
import tensorflow as tf

model = load_model(path)
graph = tf.compat.v1.get_default_graph()

with graph.as_default():
    predict_y = model.predict_classes(X)