"""Entry point for the file service."""

import fastapi
import google.cloud.logging
from absl import logging
from models import (
    DownloadFileRequest,
    DownloadFileResponse,
    SearchFileRequest,
    SearchFileResponse,
    UploadFileRequest,
    UploadFileResponse,
)
from worker import DownloadWorker, SearchWorker, UploadWorker

from common.clients import storage_client_lib
from common.models import settings as settings_lib

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

app = fastapi.FastAPI()


@app.post("/download")
def download(request: DownloadFileRequest) -> DownloadFileResponse:
    try:
        kwargs = request.dict()
        settings = settings_lib.Settings()
        worker = DownloadWorker(settings=settings)
        content, mimetype, filename = worker.execute(**kwargs)
        return {"content": content, "mimetype": mimetype, "filename": filename}
    except storage_client_lib.StorageClientError as err:
        logging.error(
            "FileServiceWorker: An error occured trying to download file %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err


@app.post("/upload")
def upload(request: UploadFileRequest) -> UploadFileResponse:
    try:
        kwargs = request.dict()
        settings = settings_lib.Settings()
        worker = UploadWorker(settings=settings)
        file_uri = worker.execute(**kwargs)
        return {"file_uri": file_uri}
    except storage_client_lib.StorageClientError as err:
        logging.error(
            "FileServiceWorker: An error occured trying to upload file %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err


@app.post("/search")
def search(request: SearchFileRequest) -> SearchFileResponse:
    try:
        kwargs = request.dict()
        settings = settings_lib.Settings()
        worker = SearchWorker(settings=settings)
        results = worker.execute(**kwargs)
        return {"results": results}
    except storage_client_lib.StorageClientError as err:
        logging.error(
            "SearchWorker: An error occured searching for file %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err


@app.post("/list")
def list_all(request: SearchFileRequest) -> SearchFileResponse:
    del request
    try:
        settings = settings_lib.Settings()
        worker = SearchWorker(settings=settings)
        results = worker.list_all()
        return {"results": results}
    except storage_client_lib.StorageClientError as err:
        logging.error(
            "SearchWorker: An error occured listing files %s",
            err,
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail=("The server could not process the request: %s", str(err)),
        ) from err
