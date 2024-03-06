# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import base64
import io

from PIL import Image, PngImagePlugin


def decode_to_image(encoding):
    image = None
    try:
        image = Image.open(io.BytesIO(base64.b64decode(encoding)))
    except Exception as e:
        raise e
    return image

def export_pil_to_bytes(image, quality):
    with io.BytesIO() as output_bytes:
        use_metadata = False
        metadata = PngImagePlugin.PngInfo()
        for key, value in image.info.items():
            if isinstance(key, str) and isinstance(value, str):
                metadata.add_text(key, value)
                use_metadata = True
        image.save(output_bytes, format="PNG", pnginfo=(
            metadata if use_metadata else None), quality=quality if quality else 80)

        bytes_data = output_bytes.getvalue()
    return bytes_data