<div align="center">
  <img src="/assets/demo.gif" alt="Demonstration" width="480">
</div>

# ComfyUI Prompt Formatter

This is a custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that provides tools to clean, optimize, and format text prompts. It includes features like converting tags, aligning brackets, and applying weights to prompts.

## About

This project is a direct equivalent of [sd_extension-prompt_formatter](https://github.com/younyokel/sd_extension-prompt_formatter) but specifically designed for ComfyUI. This project is a fork of [uwidev's sd_extension-prompt_formatter](https://github.com/uwidev/sd_extension-prompt_formatter).

## Features

### 💫 Format Prompt
A "magic button" that optimizes your prompt by:
- Removing mismatched brackets.
- Aligning commas, brackets, and alternating patterns.
- Applying weights to bracketed text.
- Removing duplicate tokens.

### ✒️ Convert Tags
This feature converts **Danbooru-style tags** (e.g., `tag_name`) into a traditional **comma-separated format** (e.g., `tag name,`).

### ⏪ Undo Last Change
Revert the last formatting or conversion action with a single click.

## Configuration Options

The behavior of the formatter can be customized using the `config.json` file. Below are the available options:

| **Option**              | **Description**                                                                 | **Values**                     | **Default**          |
|--------------------------|---------------------------------------------------------------------------------|--------------------------------|----------------------|
| `BRACKET2WEIGHT`         | Converts multiple brackets into weights.                                        | `true`, `false`                | `true`               |
| `CONV_SPACE_UNDERSCORE`  | Controls space/underscore conversion.                                           | `"None"`, `"Spaces to underscores"`, `"Underscores to spaces"` | `"None"` |
| `BLACKLIST_FILE`         | Path to the file containing blacklisted tag patterns.                           | String (file path)             | `"blacklisted_tags.txt"` |

## Blacklist Format

The blacklist file (`blacklisted_tags.txt`) contains **regular expression patterns** to filter out unwanted tags during the conversion process. Each line can include multiple patterns separated by spaces.

### Example Blacklist:
```
tagme .*text .*bubble onomatopoeia dialogue
.*(artwork) watermark signature 20\d\d
```

Patterns are compiled as regular expressions. Tags matching these patterns will be excluded during tag conversion.

## Installation

1. Clone this repository into your `custom_nodes` directory of **ComfyUI**:
   ```bash
   git clone https://github.com/younyokel/comfyui_prompt_formatter.git
   ```

2. Restart ComfyUI server.