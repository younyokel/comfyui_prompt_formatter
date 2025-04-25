from .nodes import CLIPTextEncodeFormatter, TextOnlyFormatter, TextAppendFormatter

# ComfyUI required exports
WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS = {
    "CLIPTextEncodeFormatter": CLIPTextEncodeFormatter,
    "TextOnlyFormatter": TextOnlyFormatter,
    "TextAppendFormatter": TextAppendFormatter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CLIPTextEncodeFormatter": "CLIP Text Encode (Prompt Formatter)",
    "TextOnlyFormatter": "Prompt Formatter (Only Text)",
    "TextAppendFormatter": "Append String",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']