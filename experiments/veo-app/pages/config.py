# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import pandas as pd

import mesop as me

from components.header import header
from components.page_scaffold import (
    page_frame,
    page_scaffold,
)
from state.state import AppState


from config.default import Default


def get_config_table():
    """ Construct a table of the Defaults """
    df = pd.DataFrame(
        data={
            "Config": [
                "Vertex AI",
                "Project ID",
                "Location",
                "Model ID",
                "Veo Project",
                "Veo Model ID",
                "Veo Experimental Model ID",
                "Video Bucket",
                "Image Bucket",
            ],
            "Value": [
                Default.INIT_VERTEX,
                Default.PROJECT_ID,
                Default.LOCATION,
                Default.MODEL_ID,
                Default.VEO_PROJECT_ID,
                Default.VEO_MODEL_ID,
                Default.VEO_EXP_MODEL_ID,
                f"gs://{Default.VIDEO_BUCKET}",
                f"gs://{Default.IMAGE_BUCKET}",
            ]
        }
    )
    return df

def config_page_contents(app_state: me.state):  # pylint: disable=unused-argument
    """Configurations page content"""
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():  # pylint: disable=not-context-manager
            header("Configurations", "settings")

            me.table(
                get_config_table(),
                #on_click=on_click,
                header=me.TableHeader(sticky=True),
                columns={
                    "Config": me.TableColumn(sticky=True),
                    "Value": me.TableColumn(sticky=True),
                },
            )
            
            