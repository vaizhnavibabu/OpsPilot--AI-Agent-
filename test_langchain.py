from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agent.config import settings

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    temperature=0,
)


def extract_text(content) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("text")
        ).strip()

    return str(content).strip()


response = llm.invoke(
    "Explain what an IT support ticket is in one sentence."
)

print(extract_text(response.content))