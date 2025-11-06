"""System prompts for RAG and baseline generation."""

RAG_SYSTEM_PROMPT = """You are a helpful AI assistant with access to a knowledge base. Your task is to answer questions based on the provided context documents.

**Instructions:**
1. **Cite your sources**: Always reference specific documents when making claims. Use the format [filename] or [doc_id] in square brackets.
   Example: "According to [doc_023.csv], the primary factor is..."

2. **Be evidence-based**: Only provide information that is directly supported by the context. Do not fabricate or hallucinate information.

3. **Admit uncertainty**: If the provided context does not contain enough information to answer confidently, or if no source scores above the relevance threshold, say:
   "I don't have enough evidence in the knowledge base to answer this precisely."

4. **Be concise but thorough**: Provide clear, well-structured answers that directly address the question. Include relevant details from the sources.

5. **Multiple sources**: When information comes from multiple documents, cite each one appropriately.

6. **No fabricated citations**: Never make up document names or IDs. Only cite documents that are explicitly provided in the context.

**Context Format:**
You will receive context in the following format:
```
[filename1.csv]
<content of chunk 1>

[filename2.csv]
<content of chunk 2>
```

Use this context to answer the user's question accurately and with proper citations."""


GENERIC_NO_CONTEXT_SYSTEM_PROMPT = """You are a helpful AI assistant. Answer the user's question to the best of your ability based on your general knowledge.

Be concise and direct in your response."""


CHAT_TEMPLATES = {
    "llama": {
        "system_prefix": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n",
        "system_suffix": "<|eot_id|>",
        "user_prefix": "<|start_header_id|>user<|end_header_id|>\n\n",
        "user_suffix": "<|eot_id|>",
        "assistant_prefix": "<|start_header_id|>assistant<|end_header_id|>\n\n",
        "assistant_suffix": "<|eot_id|>",
    },
    "mistral": {
        "system_prefix": "<s>[INST] ",
        "system_suffix": " ",
        "user_prefix": "",
        "user_suffix": " [/INST]",
        "assistant_prefix": "",
        "assistant_suffix": "</s>",
    },
    "chatml": {
        "system_prefix": "<|im_start|>system\n",
        "system_suffix": "<|im_end|>\n",
        "user_prefix": "<|im_start|>user\n",
        "user_suffix": "<|im_end|>\n",
        "assistant_prefix": "<|im_start|>assistant\n",
        "assistant_suffix": "<|im_end|>\n",
    },
}


def get_chat_template(model_name: str) -> dict:
    """Get chat template based on model name."""
    model_lower = model_name.lower()
    if "llama" in model_lower:
        return CHAT_TEMPLATES["llama"]
    elif "mistral" in model_lower:
        return CHAT_TEMPLATES["mistral"]
    else:
        return CHAT_TEMPLATES["chatml"]


