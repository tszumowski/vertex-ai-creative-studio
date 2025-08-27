# Plan: Add "Generate Audio" Toggle for Veo

This plan outlines the steps required to add a user-facing toggle on the Veo page to enable or disable audio generation for the final video. This feature will be restricted to models that support it (e.g., "Veo3").

### 1. Risk Analysis

*   **UI Layout Disruption:** Adding a new control could misalign or break the existing layout of the generation controls panel.
    *   **Mitigation:** The new toggle will be placed carefully within the existing component structure. I will ensure it is conditionally rendered to avoid affecting models that do not support this feature.
*   **Incorrect API Parameter:** The backend API might reject the request if the `generateAudio` parameter is sent for a model that doesn't support it.
    *   **Mitigation:** I will add a `supports_audio_generation` flag to the model configurations in `config/veo_models.py`. The UI toggle will only appear, and the API parameter will only be sent, if this flag is `True` for the selected model.
*   **Incomplete Feature Implementation:** The feature is not complete if the audio status isn't saved and displayed back to the user.
    *   **Mitigation:** The plan explicitly includes steps to update the `MediaItem` data model, save the `has_audio` status to Firestore, and display this information in the media library.

### 2. Implementation Steps

**Phase 1: Configuration & State Management**

1.  **Update Model Configuration (`config/veo_models.py`):** I will add a `supports_audio_generation: bool` attribute to the `VeoModelConfig` dataclass. This will be set to `True` only for the "Veo3" model.
2.  **Update Page State (`state/veo_state.py`):** I will add a `generate_audio: bool = False` field to the `PageState` class to hold the toggle's current state.

**Phase 2: Frontend UI**

1.  **Modify Generation Controls (`components/veo/generation_controls.py`):** I will add a `me.slide_toggle` component labeled "Generate audio". This toggle will be conditionally rendered only when `get_veo_model_config(state.veo_model).supports_audio_generation` is `True`. An event handler will be created to update the `state.generate_audio` field.

**Phase 3: Backend & API Integration**

1.  **Update Model Logic (`models/veo.py`):** The `generate_video` function will be modified to accept a `generate_audio: bool` parameter. This parameter will be added to the API request payload sent to the Veo model.
2.  **Update Page Logic (`pages/veo.py`):** The `on_click_generate` event handler will be updated to pass the `state.generate_audio` value to the `generate_video` function.

**Phase 4: Data Persistence & Library Display**

1.  **Update Data Model (`common/metadata.py`):** I will add a `has_audio: bool` field to the `MediaItem` dataclass.
2.  **Save to Firestore (`pages/veo.py`):** When a video is generated, the value of `state.generate_audio` will be saved to the new `has_audio` field in the video's Firestore document.
3.  **Update Library (`pages/library.py`):** The library will be updated to fetch the `has_audio` field and display a visual indicator (e.g., a speaker icon or text) in the details view for videos that have audio.

### 3. Validation Steps

1.  **UI Validation:**
    *   **Verify Conditional Display:** Confirm the "Generate audio" toggle is visible only when the "Veo3" model is selected and hidden for all other models.
    *   **Verify State Change:** Confirm the toggle can be switched on and off.
2.  **API Validation:**
    *   **Verify API Payload:** I will add temporary logging to confirm that the `generateAudio: true` parameter is correctly added to the API request only when the toggle is on and the model is "Veo3".
3.  **Data Validation:**
    *   **Verify Firestore Data:** After generation, I will confirm that the `has_audio` field in the corresponding Firestore document is correctly set to `true` or `false`.
4.  **Library Validation:**
    *   **Verify Library Display:** I will navigate to the library and confirm that a video generated with audio has a clear indicator, and a video without audio does not.
