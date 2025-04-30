from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict
from server import PromptServer
from aiohttp import web

from .prompt_formatter import format_prompt, convert_tags

# Route to handle text requests
@PromptServer.instance.routes.post("/prompt_formatter/format_prompt")
async def route_format_prompt(request):
    json_data = await request.json()
    result = {"success": False}
    
    if (text := json_data.get("text")) is not None:
        # Perform the text formatting
        formatted_prompt = format_prompt(text)
        result = {
            "success": True,
            "formatted_prompt": formatted_prompt
        }
    
    return web.json_response(result)

@PromptServer.instance.routes.post("/prompt_formatter/convert_tags")
async def route_convert_tags(request):
    json_data = await request.json()
    result = {"success": False}
    
    if (text := json_data.get("text")) is not None:
        # Perform the tag conversion
        converted_prompt = convert_tags(text)
        result = {
            "success": True,
            "formatted_prompt": converted_prompt
        }
    
    return web.json_response(result)

# Nodes
class CLIPTextEncodeFormatter(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(s) -> InputTypeDict:
        return {
            "required": {
                "text": (IO.STRING, {"multiline": True, "dynamicPrompts": True, "tooltip": "The text to be encoded."}),
                "clip": (IO.CLIP, {"tooltip": "The CLIP model used for encoding the text."})
            }
        }
    RETURN_TYPES = (IO.CONDITIONING,)
    OUTPUT_TOOLTIPS = ("A conditioning containing the embedded text used to guide the diffusion model.",)
    FUNCTION = "encode"

    CATEGORY = "prompt_formatter"
    DESCRIPTION = "Encodes a text prompt using a CLIP model into an embedding that can be used to guide the diffusion model towards generating specific images."

    def encode(self, clip, text):
        if clip is None:
            raise RuntimeError("ERROR: clip input is invalid: None\n\nIf the clip is from a checkpoint loader node your checkpoint does not contain a valid clip or text encoder model.")
        tokens = clip.tokenize(text)
        return (clip.encode_from_tokens_scheduled(tokens), )
    
class TextOnlyFormatter:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": (IO.STRING, {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "tooltip": "The raw text prompt to pass through or format."
                }),
            }
        }

    RETURN_TYPES = (IO.STRING,)
    OUTPUT_TOOLTIPS = ("Returns the raw text input for use in further processing.",)
    FUNCTION = "passthrough"

    CATEGORY = "prompt_formatter"
    DESCRIPTION = "A simple node that returns the input text as-is. Useful for debugging or chaining text-based operations."

    def passthrough(self, text):
        return (text,)

class TextAppendFormatter():
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string1": ("STRING", {"default": "", "forceInput": True, "tooltip": "First string to append."}),
                "string2": ("STRING", {"default": "", "forceInput": True, "tooltip": "Second string to append."}),
                "comma": ("BOOLEAN", {"default": True, "tooltip": "Add comma between strings."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "combine"
    CATEGORY = "prompt_formatter"
    DESCRIPTION = "Appends two strings together cleanly, removing unnecessary commas, spaces, or other artifacts."

    def combine(self, string1, string2, comma):
        combined = f"{string1.rstrip(' ,')}{', ' if comma else ' '}{string2.lstrip(' ,')}"
        return (combined,)
