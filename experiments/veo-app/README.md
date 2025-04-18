# Experiment: Veo app

This is the initial experiment for the Veo addition to Vertex AI Creative Studio.

![](./assets/veo-app.png)


Current featureset
* Create a video from a prompt (text to video)
* Firestore indexing of generated videos

Future featureset

* Prompt rewriter
* Library display of generated videos from Firestore indexing of stored videos
* Image to video
* Advanced Veo features
* Integration into main GenMedia Creative Studio



It's built using the Mesop scaffold for Studio style apps.


## Prerequisites


### Cloud Firestore

We will be using [Cloud Firestore](https://firebase.google.com/docs/firestore), a NoSQL cloud database that is part of the Firebase ecosystem and built on Google Cloud infrastructure, to save generated image metadata and ELO scores for the leaderboard.

> If you're new to Firebase, a great starting point is [here](https://firebase.google.com/docs/projects/learn-more#firebase-cloud-relationship).

Go to your Firebase project and create a database. Instructions on how to do this can be found [here](https://firebase.google.com/docs/firestore/quickstart).

Next do the following steps:

1. Create a collection called `genmedia`. This is the default collection name. 

The name of the collections can be changed via environment variables in the `.env` file, by setting the environment variable `GENMEDIA_COLLECTIONS_NAME` to your chosen collection name.




### Python virtual environment

A python virtual environment, with required packages installed.

Using [uv](https://github.com/astral-sh/uv):

```
# sync a virtual environment
uv sync # or: uv sync --upgrade
# activate the virtual environ,ent
. venv/bin/activate
```

### Application Environment variables

Use the included dotenv.template and create a `.env` file with your specific environment variables. See the dotenv.template for the defaults.

Only one environment variable is required:

* `PROJECT_ID` your Google Cloud Project ID, obtained via `gcloud config get project`




## GenMedia Creative Studio - Veo Studio

Start the app to create videos

```
mesop main.py
```

