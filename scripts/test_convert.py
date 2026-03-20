import os
from huggingface_hub import hf_hub_download

print('downloading model')
keras_path = hf_hub_download(repo_id='PAMify001/BotanIQ_Model', filename='botaniq_model.keras')
print('downloaded', keras_path)

import tensorflow as tf
print('tf', tf.__version__)

model = tf.keras.models.load_model(keras_path)
print('model loaded', model)
print('inputs', model.inputs)

import tf2onnx

spec = (tf.TensorSpec(model.inputs[0].shape, tf.float32),)
print('spec', spec)

print('converting...')
onnx_path = 'botaniq_model.onnx'
model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=17, output_path=onnx_path, large_model=True, fold_const=True)

print('converted:', onnx_path, os.path.exists(onnx_path), os.path.getsize(onnx_path))
