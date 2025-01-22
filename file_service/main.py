"""Entry point for the file service."""

import fastapi
import google.cloud.logging
from absl import logging
from models import (
    DownloadFileRequest,
    DownloadFileResponse,
    UploadFileRequest,
    UploadFileResponse,
)
from worker import DownloadWorker, UploadWorker

from common.clients import storage_client_lib

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

app = fastapi.FastAPI()


@app.post("/download")
def download(request: DownloadFileRequest) -> DownloadFileResponse:
    try:
        kwargs = request.dict()
        worker = DownloadWorker(settings=None)
        file_string = worker.execute(**kwargs)
        return {"file_string": file_string}
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
        worker = UploadWorker(settings=None)
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
