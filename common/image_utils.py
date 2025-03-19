import io

from absl import logging
from PIL import Image as PIL_Image
from vertexai.preview.vision_models import Image


def pad_to_target_size(
    source_image: Image,
    target_size: tuple[int, int] = (1536, 1536),
    mode: str = "RGB",
    vertical_offset_ratio: int = 0,
    horizontal_offset_ratio: int = 0,
    fill_val: int = 255,
) -> PIL_Image:
    """Pads an image for outpainting."""
    orig_image_size_w, orig_image_size_h = source_image.size
    target_size_w, target_size_h = target_size
    x_pos = (target_size_w - orig_image_size_w) // 2
    y_pos = (target_size_h - orig_image_size_h) // 2
    insert_pt_x = x_pos + int(horizontal_offset_ratio * x_pos)
    insert_pt_y = y_pos + int(vertical_offset_ratio * y_pos)
    insert_pt_x = min(insert_pt_x, target_size_w - orig_image_size_w)
    insert_pt_y = min(insert_pt_y, target_size_h - orig_image_size_h)

    if mode == "RGB":
        source_image_padded = PIL_Image.new(
            mode,
            target_size,
            color=(fill_val, fill_val, fill_val),
        )
    elif mode == "L":
        source_image_padded = PIL_Image.new(mode, target_size, color=(fill_val))
    else:
        raise ValueError("source image mode must be RGB or L.")

    source_image_padded.paste(source_image, (insert_pt_x, insert_pt_y))
    return source_image_padded


def pad_image_and_mask(
    ref_image: Image,
    target_size: tuple[int, int] = (1536, 1536),
    vertical_offset_ratio: int = 0,
    horizontal_offset_ratio: int = 0,
) -> tuple[PIL_Image, PIL_Image]:
    """Pads and resizes image and mask to the same target size."""
    image_vertex = ref_image._pil_image
    mask_vertex = PIL_Image.new("L", ref_image._pil_image.size, 0)
    image_vertex.thumbnail(target_size)
    mask_vertex.thumbnail(target_size)

    image_vertex = pad_to_target_size(
        image_vertex,
        target_size=target_size,
        mode="RGB",
        vertical_offset_ratio=vertical_offset_ratio,
        horizontal_offset_ratio=horizontal_offset_ratio,
        fill_val=0,
    )
    mask_vertex = pad_to_target_size(
        mask_vertex,
        target_size=target_size,
        mode="L",
        vertical_offset_ratio=vertical_offset_ratio,
        horizontal_offset_ratio=horizontal_offset_ratio,
        fill_val=255,
    )
    return image_vertex, mask_vertex


def get_bytes_from_pil(image: PIL_Image) -> bytes:
    byte_io_png = io.BytesIO()
    image.save(byte_io_png, "PNG")
    return byte_io_png.getvalue()


def overlay_mask(
    image: Image,
    mask: Image,
    alpha: float = 0.5,
) -> Image:
    """Overlays a mask on an image.  Handles Vertex AI Image objects correctly.

    Args:
        image: The base image (vertexai.preview.vision_models.Image).
        mask: The mask image (vertexai.preview.vision_models.Image).
            Should have the same dimensions as the image.
        alpha: The transparency of the mask overlay (0.0 to 1.0).

    Returns:
        A PIL Image object with the mask overlaid, or None if there's an error.
    """
    image_bytes = image._image_bytes
    image_pil = PIL_Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    mask_bytes = mask._image_bytes
    mask_pil = PIL_Image.open(io.BytesIO(mask_bytes)).convert(
        "RGBA",
    )
    if image_pil.size != mask_pil.size:
        logging.info("Resizing mask to image size.")
        mask_pil = mask_pil.resize(image_pil.size)
    if image_pil.mode != mask_pil.mode:
        logging.info("Converting mask to image mode.")
        mask_pil = mask_pil.convert(image_pil.mode)
    blended_pil = PIL_Image.blend(image_pil, mask_pil, alpha=alpha)
    return Image(get_bytes_from_pil(blended_pil))


def get_aspect_ratio_string(image: Image) -> str:
    """Calculates the aspect ratio of a Vertex AI Image object.

    Args:
        image: The Vertex AI Image object.

    Returns:
        The aspect ratio as a string, or None if the image has no dimensions.
    """
    try:
        width, height = image._pil_image.size

        def _find_common_denominator(width: int, height: int) -> int:
            """Helper function to find the greatest common divisor."""
            while height:
                width, height = height, width % height
            return width

        common_divisor = _find_common_denominator(width, height)
        simplified_width = width // common_divisor
        simplified_height = height // common_divisor

        return f"{simplified_width}:{simplified_height}"

    except Exception as ex:
        logging.error("Error extracting aspect ratio from image: %s", ex)
