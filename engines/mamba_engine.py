import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
LLM Engine - Llama 4 Maverick via Groq + Together AI
Smart multi-provider with automatic fallback
"""

import os
from dotenv import load_dotenv
load_dotenv()

from config.settings import (
    MAMBA_MAX_TOKENS,
    MAMBA_TEMP_BALANCED,
    GROQ_MODEL,
    TOGETHER_MODEL,
    GROQ_FALLBACK_MODEL
)

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

try:
    from together import Together
    HAS_TOGETHER = True
except ImportError:
    HAS_TOGETHER = False


class Mamba2LLM:
    """
    Smart LLM: Groq (primary) -> Together AI (fallback)
    Both running Llama 4 Maverick
    Callable: result = llm("your prompt")
    """

    def __init__(
        self,
        max_tokens=MAMBA_MAX_TOKENS,
        temperature=MAMBA_TEMP_BALANCED
    ):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.providers = []
        self.active = None

        groq_key = os.getenv("GROQ_API_KEY", "")
        together_key = os.getenv("TOGETHER_API_KEY", "")

        # Priority 1: Groq (free + fastest)
        if HAS_GROQ and groq_key:
            self.providers.append({
                "name": "groq",
                "client": Groq(api_key=groq_key),
                "model": GROQ_MODEL,
                "label": "Llama 4 Maverick (Groq)"
            })
            # Also add Scout as fallback on Groq
            self.providers.append({
                "name": "groq-scout",
                "client": Groq(api_key=groq_key),
                "model": GROQ_FALLBACK_MODEL,
                "label": "Llama 4 Scout (Groq)"
            })

        # Priority 2: Together AI
        if HAS_TOGETHER and together_key:
            self.providers.append({
                "name": "together",
                "client": Together(api_key=together_key),
                "model": TOGETHER_MODEL,
                "label": "Llama 4 Maverick (Together AI)"
            })

        if self.providers:
            self.active = self.providers[0]

    def __call__(self, prompt, stop=None):
        """Make callable"""
        return self.generate(prompt, stop)

    def generate(self, prompt, stop=None):
        """Try each provider until one works"""

        if not self.providers:
            return (
                "No LLM configured. Add to .env:\n"
                "  GROQ_API_KEY=your_key (free: console.groq.com)\n"
                "  TOGETHER_API_KEY=your_key (api.together.xyz)"
            )

        errors = []

        for provider in self.providers:
            try:
                response = provider["client"].chat.completions.create(
                    model=provider["model"],
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert financial analyst "
                                "and Vedic astrology (Jyotish) advisor. "
                                "Provide detailed, structured, and "
                                "actionable analysis. Use tables and "
                                "clear formatting."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )

                self.active = provider
                return response.choices[0].message.content

            except Exception as e:
                errors.append(provider["name"] + ": " + str(e))
                continue

        return "All providers failed:\n" + "\n".join(errors)

    def get_info(self):
        """Current provider info"""
        if self.active:
            return {
                "provider": self.active["name"],
                "model": self.active["model"],
                "label": self.active["label"]
            }
        return {
            "provider": "none",
            "model": "none",
            "label": "Not configured"
        }


def get_factual_llm():
    """Low creativity for data analysis"""
    return Mamba2LLM(temperature=0.1)

def get_balanced_llm():
    """Moderate creativity for recommendations"""
    return Mamba2LLM(temperature=0.3)

def get_creative_llm():
    """Higher creativity for jyotish predictions"""
    return Mamba2LLM(temperature=0.5, max_tokens=8192)


if __name__ == "__main__":
    print("=" * 50)
    print("LLM ENGINE TEST")
    print("=" * 50)

    groq_key = os.getenv("GROQ_API_KEY", "")
    together_key = os.getenv("TOGETHER_API_KEY", "")
    print("Groq key: " + ("YES" if groq_key else "MISSING"))
    print("Together key: " + ("YES" if together_key else "MISSING"))

    llm = get_balanced_llm()
    info = llm.get_info()
    print("Primary: " + info["label"])
    print("Total providers: " + str(len(llm.providers)))
    print()

    print("Testing...")
    result = llm("Name top 3 Indian stocks by market cap. Be brief.")
    print("Response:")
    print(result[:500])
    print()
    print("Used: " + llm.get_info()["label"])
