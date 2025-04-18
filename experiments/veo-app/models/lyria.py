import base64

import shortuuid
import vertexai
from google.api_core.exceptions import GoogleAPIError
from google.cloud import aiplatform, storage

from config.default import Default


# Initialize Configuration
cfg = Default()
vertexai.init(project=cfg.PROJECT_ID, location=cfg.LOCATION)
aiplatform.init(project=cfg.PROJECT_ID, location=cfg.LOCATION)


def generate_music_with_lyria(prompt: str):
    """generates music with lyria"""

    LOCATION = cfg.LOCATION
    MODEL_VERSION = cfg.LYRIA_MODEL_VERSION
    PROJECT_ID = cfg.LYRIA_PROJECT_ID
    LYRIA_ENDPOINT = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_VERSION}"

    aiplatform.init(project=PROJECT_ID, location=LOCATION)

    instances = []
    instances.append({"prompt": prompt})
    parameters = {"sampleCount": 1}

    api_regional_endpoint = f"{LOCATION}-aiplatform.googleapis.com"
    client_options = {"api_endpoint": api_regional_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    print(
        f"Prediction client initiated on project {PROJECT_ID} in {LOCATION}: {LYRIA_ENDPOINT}."
    )

    try:
        response = client.predict(
            endpoint=LYRIA_ENDPOINT,
            instances=instances,
            parameters=parameters,
        )
        contents = response.predictions[0]["bytesBase64Encoded"]

        # create a file name
        my_uuid = shortuuid.uuid()
        file_name = f"lyria_generation_{my_uuid}.wav"

        # store on gcs
        destination_blob_name = store_to_gcs(
            "music", file_name, "audio/wav", contents, True
        )


        print(
            f"{destination_blob_name} with contents len {len(contents)}  uploaded to {cfg.MEDIA_BUCKET}."
        )
    except GoogleAPIError as e:
        print(f"Error: {e}")
        print(e)

    return destination_blob_name


def store_to_gcs(
    folder: str, file_name: str, mime_type: str, contents: str, decode: bool = False
):
    """store contents to GCS"""
    client = storage.Client(project=cfg.PROJECT_ID)
    bucket = client.get_bucket(cfg.MEDIA_BUCKET)
    destination_blob_name = f"{folder}/{file_name}"
    blob = bucket.blob(destination_blob_name)
    if decode:
        contents_bytes = base64.b64decode(contents)
        blob.upload_from_string(contents_bytes, content_type=mime_type)
    else:
        blob.upload_from_string(contents, content_type=mime_type)
    return f"{cfg.MEDIA_BUCKET}/{destination_blob_name}"
