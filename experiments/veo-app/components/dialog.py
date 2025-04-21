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
"""Dialog mesop component"""

from typing import Callable

import mesop as me


@me.content_component
def dialog(is_open: bool):
  """Renders a dialog component.

  The design of the dialog borrows from the Angular component dialog. So basically
  rounded corners and some box shadow.

  One current drawback is that it's not possible to close the dialog
  by clicking on the overlay background. This is due to
  https://github.com/google/mesop/issues/268.

  Args:
    is_open: Whether the dialog is visible or not.
  """
  with me.box(
    style=me.Style(
      background="rgba(0,0,0,0.4)",
      display="block" if is_open else "none",
      height="100%",
      left=0, # Ensure overlay covers from the left edge
      top=0,  # Ensure overlay covers from the top edge
      overflow_x="auto",
      overflow_y="auto",
      position="fixed", # Use fixed positioning for overlay
      width="100%",
      z_index=1000, # Ensure dialog is on top
    )
  ):
    # This box centers the dialog content vertically and horizontally
    with me.box(
      style=me.Style(
        display="flex", # Use flexbox for centering
        align_items="center", # Center vertically
        justify_content="center", # Center horizontally
        height="100%", # Take full height of the overlay
        width="100%", # Take full width of the overlay
        padding=me.Padding.all(20) # Add some padding so dialog doesn't touch edges
      )
    ):
      # This is the actual dialog box container
      with me.box(
        style=me.Style(
          background=me.theme_var("surface-container-lowest"), # Use theme variable for background
          color=me.theme_var("on-surface"), # Use theme variable for text color
          border_radius=8, # Slightly smaller radius for modern look
          box_shadow=( # Standard shadow
            "0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"
          ),
          padding=me.Padding.all(24), # Inner padding for content
          width="auto", # Let width be determined by content
          max_width="500px", # Set a max width
          display="block", # Ensure it behaves as a block
          box_sizing="border-box", # Include padding/border in width/height
        )
      ):
        me.slot() # Content goes here

@me.content_component
def dialog_actions():
  """Helper component for rendering action buttons so they are right aligned.

  This component is optional. If you want to position action buttons differently,
  you can just write your own Mesop markup.
  """
  with me.box(
    style=me.Style(
      display="flex",
      justify_content="flex-end", # Align buttons to the end (right)
      margin=me.Margin(top=24), # Space above the actions
      gap=8 # Space between buttons if multiple are added
    )
  ):
    me.slot() # Action buttons go here
