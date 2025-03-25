# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mesop as me
from pages import constants


@me.stateclass
class AppState:
    """Mesop Application State."""

    theme_mode: str = "light"
    sidenav_open: bool = True

    rewriter_prompt: str = ""
    rewriter_prompt_placeholder: str = constants.REWRITER_PROMPT.strip()
    textarea_key: int = 0

    critic_prompt: str = ""
    critic_prompt_placeholder: str = constants.CRITIC_PROMPT.strip()

    user_email: str = ""
    user_agent: str = ""
