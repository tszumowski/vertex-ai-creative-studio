import enum


class EditMode(enum.Enum):
    EDIT_MODE_INPAINT_INSERTION = "inpainting-insert"
    EDIT_MODE_OUTPAINT = "outpainting"
    EDIT_MODE_INPAINT_REMOVAL = "inpainting-remove"
    EDIT_MODE_PRODUCT_IMAGE = "product-image"
    EDIT_MODE_BGSWAP = "background-swap"
    EDIT_MODE_CONTROLLED_EDITING = "controlled-editing"
