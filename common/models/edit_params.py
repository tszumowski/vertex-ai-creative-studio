from common.models import edit_mode


class EditParams:
    def __init__(self, edit_mode: edit_mode.EditMode) -> None:
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
