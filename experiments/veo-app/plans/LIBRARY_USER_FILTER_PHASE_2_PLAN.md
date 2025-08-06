# Phase 2: Library Chooser Components User Filter (Detailed Plan)

**Objective:** Extend the "Mine" vs. "All" user filter to the library chooser components (`infinite_scroll_library.py`, `library_chooser_button.py`, etc.) that are used in other pages (e.g., VTO, Imagen). This will be tested in isolation before being integrated into the main application.

---

### Core Technical Strategy & Lessons Learned

This phase builds directly on the work completed in Phase 1. The core principle is to **reuse the existing filtering logic** and avoid duplicating code.

1.  **The Filtering Logic is Done:** The `get_media_for_page` function in `common/metadata.py` already contains the necessary Python-based logic to filter media items by `user_email`. We will not modify this further.

2.  **Firestore Composite Index Limitation:** We learned in Phase 1 that we **must not** add a `.where("user_email", ...)` clause to the Firestore query, as it conflicts with the `order_by("timestamp")` clause and will fail without a specific composite index. The current approach of filtering in Python is the correct one for this application.

3.  **The Goal is Parameter Propagation:** The primary technical task of Phase 2 is to **propagate the user's filter choice (e.g., "mine") from the UI down to the `get_media_for_page` function.** This will be achieved by adding a new `user_filter: str = "all"` parameter to the function signatures of all necessary components in the call chain.

---

### Step 1: Analysis of Component Hierarchy

- **Action:** Identify the complete call chain from the user-facing page (e.g., VTO) to the data-fetching function.
- **Example Chain:** `pages/vto.py` -> `components/library/library_chooser_button.py` -> `components/library/infinite_scroll_library.py` -> `common/metadata.py::get_media_for_page()`.
- **Goal:** Create a definitive list of all functions in this chain that must be modified to accept and pass down the new `user_filter` parameter.

### Step 2: Isolated Testing & Implementation (`pages/test_infinite_scroll.py`)

- **Action:** Use `pages/test_infinite_scroll.py` as a sandbox to safely implement and verify the changes before touching production-like pages.
- **Implementation Details:**
  1.  Add the "All" vs. "Mine" `me.button_toggle` to the UI of the test page.
  2.  Add a new `user_filter: str = "all"` parameter to the `infinite_scroll_library` component's function signature.
  3.  In the test page, connect the state of the new toggle to this new `user_filter` parameter when calling the component.
  4.  Verify that the component correctly filters the results by observing the displayed items when toggling between "All" and "Mine".

### Step 3: Refactoring the Component Chain

- **Action:** Based on the successful test, add the `user_filter: str = "all"` parameter to all the functions identified in Step 1.
- **Implementation Details:** This is a mechanical but critical step. Each function in the chain will be modified to accept the new parameter and pass it to the next function in the chain.

### Step 4: Final Integration into Production Pages (e.g., VTO, Imagen)

- **Action:** Add the "All" vs. "Mine" toggle to the UI where the library chooser is invoked (e.g., inside the dialog that appears when a user clicks "Choose from Library").
- **Implementation Details:** Connect the state of this new toggle to the newly added `user_filter` parameter on the chooser component.

---

### Key Considerations & Safeguards

- **Regression Prevention (CRITICAL):** The default value for the new `user_filter` parameter **must always be `"all"`**. This is the primary safeguard. Any page that uses the library chooser that we have not yet updated will call the components without the new parameter. The function will use the default value, and the query will behave exactly as it did before, showing all results and preventing any regressions.

- **UX & Performance Note:** The plan must acknowledge the known behavior of the client-side filtering approach. When a user has the "Mine" filter selected, a "page" of results in the infinite scroll might appear smaller than a full page. This happens because the system fetches a full page from the database (e.g., 20 items) and then filters them in Python. If only 5 of those 20 items belong to the user, only 5 will be displayed. This is the intentional and accepted design trade-off to avoid database indexing complexity and is not considered a bug.