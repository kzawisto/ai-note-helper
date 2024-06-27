#
from openai import OpenAI


class LLMApi:
    def __init__(self,settings):
        self.settings = settings
        self.system_prompt = (
                'Please make your answer concise and coherent'
        )
    
    def generate(
        self, text: str, max_tokens: int = 4096, temperature: float = 0.3
        ) -> str:
        self.openai = OpenAI(
            api_key=self.settings['api_key'],
            base_url=self.settings['api_url'],
        )

        chat_completion = self.openai.chat.completions.create(
            model=self.settings['api_model'],
            messages=[{'role':'system','content':self.system_prompt},{"role": "user", "content": text}],
            max_tokens = max_tokens, temperature=temperature
        )
        result= chat_completion.choices[0].message.content
        print(chat_completion)
        print(result)
        return result

class LLMApiOpenAI:
    def __init__(self, settings):
        self.settings = settings
        self.system_prompt = (
                'Please make your answer concise and coherent'
        )
    
    def generate(
        self, text: str, max_tokens: int = 4096, temperature: float = 0.3
        ) -> str:

        self.openai = OpenAI(
            api_key=self.settings['api_key'],
        )

        chat_completion = self.openai.chat.completions.create(
            model=self.settings['api_model'],#"gpt-3.5-turbo-0125",
            messages=[{'role':'system','content':self.system_prompt},{"role": "user", "content": text}],
            max_tokens = max_tokens, temperature=temperature
        )
        result= chat_completion.choices[0].message.content
        print(chat_completion)
        print(result)
        return result


class LLM:
    """
    LLM class encapsulates the logic to load a pre-trained language model and generate text based on input prompts.
    """

    def __init__(self, settings) -> None:
        print("INFO: Loading model...")
        self.settings=settings
        self.system_prompt = (
            "You are responsible for rephrasing, summarizing, or editing various text snippets to make them more "
            "concise, coherent, and engaging. You are also responsible for writing emails, messages, and other forms "
            "of communication."
        )
        from llama_cpp import Llama
        self.llm = Llama.from_pretrained(
            repo_id="MaziyarPanahi/Qwen2-1.5B-Instruct-GGUF",
            filename="Qwen2-1.5B-Instruct.Q4_K_M.gguf",
            local_dir="./models",
            n_ctx=4096,
            n_gpu_layers=-1,
            flash_attn=True,
            cont_batching=True,
            verbose=False,
        )
        print("INFO: Model loaded successfully.")

    def generate(
        self, text: str, max_tokens: int = 4096, temperature: float = 0.3
    ) -> str:
        """
        Generate a response from the language model based on the provided text.

        :param text: Input text prompt for the model.
        :param max_tokens: Maximum number of tokens to generate.
        :param temperature: Sampling temperature for generation.
        :return: Generated text response.
        """
        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"]
