# Experiment: Veo app

This is the initial experiment for the Veo addition to Vertex AI Creative Studio.

![](./assets/veo-app.png)


Current featureset
* Create a video from a prompt (text to video)
* Library: Display the previous stored videos from Firestore index

Future featureset

* Image to video
* Prompt rewriter
* Additional Veo features: seed, negative prompt, person generation control
* Advanced Veo features
* Integration into main GenMedia Creative Studio



It's built using the Mesop scaffold for Studio style apps.


## Prerequisites


### Cloud Firestore

We will be using [Cloud Firestore](https://firebase.google.com/docs/firestore), a NoSQL cloud database that is part of the Firebase ecosystem and built on Google Cloud infrastructure, to save generated video metadata for the Library.

> If you're new to Firebase, a great starting point is [here](https://firebase.google.com/docs/projects/learn-more#firebase-cloud-relationship).

Go to your Firebase project and create a database. Instructions on how to do this can be found [here](https://firebase.google.com/docs/firestore/quickstart).

Next do the following steps:

* Create a collection called `genmedia`. This is the default collection name. 

The name of the collection can be changed via environment variables in the `.env` file, by setting the environment variable `GENMEDIA_COLLECTIONS_NAME` to your chosen collection name.

### Google Cloud Storage bucket

You'll need a Google Cloud Storage bucket to hold the videos created and images uploaded.

By default, if you don't specify a bucket name in one of the applicaiton environment variables below, it'll be YOUR_PROJECT_NAME-assets.

You can create this like so:

```bash
export PROJECT_ID=$(gcloud config get project)
gcloud storage mb -l us-central gs://${PROJECT_ID}-assets
```




### Python virtual environment

A python virtual environment, with required packages installed.

Using the [uv](https://github.com/astral-sh/uv) virtual environment and package manager:

```
# sync the requirements to a virtual environment
uv sync
# activate the virtual environment
. .venv/bin/activate
```

If you've done this before, you can also use the command `uv sync --upgrade` to check for any package version upgrades.


### Application Environment variables

Use the included dotenv.template and create a `.env` file with your specific environment variables. See the dotenv.template for the defaults.

Only one environment variable is required:

* `PROJECT_ID` your Google Cloud Project ID, obtained via `gcloud config get project`




## GenMedia Creative Studio - Veo Studio

Start the app to create videos

```
mesop main.py
```

