from llama_cpp import Llama

llm = Llama(
    model_path=r"D:\SE Modding\DSV Modding\DSV-RP-Bot\LLM\models\mistral-7b-instruct-v0.1.Q5_K_M.gguf",
    n_ctx=32768,
    n_threads=8
)
print("🧠 Model max context length:", llm.context_params.n_ctx)

output = llm("You are the diplomatic AI of the Iron Hegemony. Why are you attacking the player?", max_tokens=128)
print(output["choices"][0]["text"])

### MODEL PATHS
# Mistral Q5: D:\SE Modding\DSV Modding\DSV-RP-Bot\LLM\models\mistral-7b-instruct-v0.1.Q5_K_M.gguf
# OpenHermes Mistral Q4: D:\SE Modding\DSV Modding\DSV-RP-Bot\LLM\models\openhermes-2.5-mistral-7b-16k.Q4_K_M.gguf
# OpenHermes Mistral Q5: D:\SE Modding\DSV Modding\DSV-RP-Bot\LLM\models\openhermes-2.5-mistral-7b-16k.Q5_K_M.gguf
# MythoMax Q4: D:\SE Modding\DSV Modding\DSV-RP-Bot\LLM\models\mythomax-l2-13b.Q4_K_M.gguf
# MythoMax Q5: D:\SE Modding\DSV Modding\DSV-RP-Bot\LLM\models\mythomax-l2-13b.Q5_K_M.gguf