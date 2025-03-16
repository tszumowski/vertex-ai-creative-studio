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

    user: str = ""
