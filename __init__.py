from .comfyui_prompt_formatter import CLIPTextEncodeFormatter

WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS = {
    "CLIPTextEncodeFormatter": CLIPTextEncodeFormatter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CLIPTextEncodeFormatter": "CLIP Text Encode (Prompt Formatter)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
