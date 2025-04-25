import { app } from "../../scripts/app.js";

const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

async function handlePromptRequest(action, text) {
    try {
        const response = await fetch(`/prompt_formatter/${action}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        });
        
        if (!response.ok) {
            throw new Error(`Error: ${response.status} - ${response.statusText}`);
        }
        
        const result = await response.json();
        if (result.success) {
            return result.formatted_prompt;
        } else {
            throw new Error(`Failed to ${action.replace('_', ' ')} text`);
        }
    } catch (error) {
        console.error(`API call to ${action.replace('_', ' ')} text failed:`, error);
        return text;
    }
}

app.registerExtension({
    name: "prompt.formatter",
    nodeCreated(node) {
        if (node.comfyClass === "CLIPTextEncodeFormatter" || node.comfyClass === "TextOnlyFormatter") {
            node.addWidget("button", "💫 Format Prompt", "", async () => {
                const textWidget = findWidgetByName(node, "text");
                const formattedPrompt = await handlePromptRequest("format_prompt", textWidget.value);
                textWidget.value = formattedPrompt;
            });
            
            node.addWidget("button", "✒️ Convert Tags", "", async () => {
                const textWidget = findWidgetByName(node, "text");
                const convertedPrompt = await handlePromptRequest("convert_tags", textWidget.value);
                textWidget.value = convertedPrompt;
            });
            
            node.addWidget("button", "⏪ Undo Last Change", "", async () => {
                const textWidget = findWidgetByName(node, "text");
                const undidPrompt = await handlePromptRequest("undo_convert", textWidget.value);
                textWidget.value = undidPrompt;
            });
        }
    },
});
