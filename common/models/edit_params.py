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

"""Defines the Edit Params class."""

from common.models import edit_mode


class EditParams:
    """A helper class to store edit params."""

    def __init__(self, edit_mode: edit_mode.EditMode) -> None:
        """Instantiates the EditParams class.

        Args:
            edit_mode: The edit mode.
        """
        self.edit_mode = edit_mode

    def get_edit_mode(self) -> str:
        return self.edit_mode.name

    def get_dilation(self) -> float:
        if self.edit_mode == edit_mode.EditMode.EDIT_MODE_OUTPAINT:
            return 0.03
        if self.edit_mode == edit_mode.EditMode.EDIT_MODE_BGSWAP:
            return 0.0
        return 0.01

    def get_base_steps(self) -> int:
        if self.edit_mode == edit_mode.EditMode.EDIT_MODE_OUTPAINT:
            return 35
        if self.edit_mode == edit_mode.EditMode.EDIT_MODE_INPAINT_INSERTION:
            return 35
        if self.edit_mode == edit_mode.EditMode.EDIT_MODE_INPAINT_REMOVAL:
            return 12
        if self.edit_mode == edit_mode.EditMode.EDIT_MODE_BGSWAP:
            return 75
        return 35
