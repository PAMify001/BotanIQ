"""Convert the Keras model in the Hugging Face repo to ONNX format.

Run this locally (where TensorFlow is available). It will:
  1) Download botaniq_model.keras from your HF repo
  2) Convert it to ONNX using tf2onnx
  3) Save to botaniq_model.onnx
  4) (Optional) upload to the same HF repo if HF_TOKEN is set.

Usage:
  python scripts/convert_to_onnx.py

After running, upload the generated botaniq_model.onnx to your HF repo (or let this script do it if you configure HF_TOKEN).
"""

import os

from huggingface_hub import hf_hub_download, HfApi

REPO_ID = "PAMify001/BotanIQ_Model"
KERAS_FILENAME = "botaniq_model.keras"
ONNX_FILENAME = "botaniq_model.onnx"


def main():
    try:
        print("Downloading Keras model from Hugging Face...")
        keras_path = hf_hub_download(repo_id=REPO_ID, filename=KERAS_FILENAME)
        print("Keras model downloaded to", keras_path)

        import tensorflow as tf
        import tf2onnx

        print("Loading Keras model...")
        model = tf.keras.models.load_model(keras_path)

        # Choose a dummy input shape based on model input spec.
        # We'll try to infer from the model.
        input_signature = None
        if hasattr(model, "inputs") and model.inputs:
            input_shape = model.inputs[0].shape
            input_shape = [dim if dim is not None else 1 for dim in input_shape]
            input_signature = (tf.TensorSpec(input_shape, tf.float32),)
            print("Inferred input signature:", input_signature)

        print("Converting to ONNX...")
        spec = input_signature
        if spec is None:
            spec = (tf.TensorSpec((1, 256, 256, 3), tf.float32),)
            print("Using fallback input signature:", spec)

        model_proto, external_tensor_storage = tf2onnx.convert.from_keras(
            model,
            input_signature=spec,
            opset=17,
            output_path=ONNX_FILENAME,
        )

        print("Saved ONNX model to", ONNX_FILENAME)

        # Optionally upload to Hugging Face
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token:
            print("Uploading ONNX model to Hugging Face repo...")
            api = HfApi()
            api.upload_file(
                path_or_fileobj=ONNX_FILENAME,
                path_in_repo=ONNX_FILENAME,
                repo_id=REPO_ID,
                token=hf_token,
                repo_type="model",
            )
            print("Upload complete.")
        else:
            print("HF_TOKEN not set, skipping upload.\n"
                  "Please upload the file manually to the repo or set HF_TOKEN.")

    except Exception as e:
        import traceback
        print("ERROR during conversion:", e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
