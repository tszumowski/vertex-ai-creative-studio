# Independent tests

Not python tests.


AI Platform Predict Client (not working)
```
export OUTPUT_GCS=gs://genai-blackbelt-fishfooding-ghchinoy/videos
PROJECT_ID=veo-testing python veo_simple.py
```

or

HTTP example

```
PROJECT_ID=veo-testing python generate_video.py
```



```
export BEARER=$(gcloud auth print-access-token)
export OP=projects/veo-testing/locations/us-central1/publishers/google/models/veo-2.0-generate-exp/operations/4e76caef-ddf3-4bf6-b11d-257097771e5d
curl -H "Authorization: Bearer ${BEARER}" -H "x-goog-user-project: veo-testing" "https://us-central1-aiplatform.googleapis.com/v1beta1/${OP}:fetchPredictOperation"
```