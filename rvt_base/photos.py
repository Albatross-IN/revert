"""Photos as they travel to a screen. A list shows a small copy and a photo opened to be looked at
a screen-size one: a phone on site should not fetch a camera file of several megabytes for a
thumbnail. The stored photo is never changed; it stays as it was taken."""
from odoo.tools.image import image_process

# the longest side, in pixels
SIZES = {"thumb": 480, "view": 1600}


def sized(content, size=None):
    """``content`` (bytes) made no larger than the named size, as a JPEG. Without a known size,
    or when the file is not an image that can be read, it is returned as it is."""
    side = SIZES.get(size or "")
    if not side or not content:
        return content
    try:
        return image_process(content, size=(side, side), quality=82, output_format="JPEG") or content
    except Exception:  # noqa: BLE001  (not a readable image: it travels as it is)
        return content
