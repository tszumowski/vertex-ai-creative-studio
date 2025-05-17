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
""" Gemini methods"""

from google.genai.types import (
    GenerateContentConfig,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from models.model_setup import GeminiModelSetup

client, model_id = GeminiModelSetup.init()
MODEL_ID = model_id


@retry(
    wait=wait_exponential(
        multiplier=1, min=1, max=10
    ),  # Exponential backoff (1s, 2s, 4s... up to 10s)
    stop=stop_after_attempt(3),  # Stop after 3 attempts
    retry=retry_if_exception_type(Exception),  # Retry on all exceptions
    reraise=True,  # re-raise the last exception if all retries fail
)
def rewriter(original_prompt: str, rewriter_prompt:str) -> str:
    """A gemini rewriter.

    Args:
        original_prompt: The original prompt to be rewritten.

    """

    full_prompt = f"{rewriter_prompt} {original_prompt}"

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=full_prompt,
            config=GenerateContentConfig(
                response_modalities=["TEXT"],
            ),
        )
        print(f"success! {response.text}")
        return response.text
    except Exception as e:
        print(f"error: {e}")
        raise  # Re-raise the exception for tenacity to handle

