import mesop as me


@me.stateclass
class AppState:
    """Mesop Application State."""

    theme_mode: str = "light"
    sidenav_open: bool = True
    welcome_message: str = ""
    name: str = "World"
