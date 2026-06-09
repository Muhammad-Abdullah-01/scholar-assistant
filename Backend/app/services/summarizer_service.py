# # from langchain_core.prompts import PromptTemplate
# # from langchain_openai import ChatOpenAI
# # from langchain_core.output_parsers import StrOutputParser
# # from dotenv import load_dotenv
# # import asyncio

# # load_dotenv()

# # # Shared model instance
# # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
# # parser = StrOutputParser()

# # # ---------------------------
# # # 0️⃣ Utility: Detect user instructions
# # # ---------------------------
# # def detect_user_instructions(prompt: str) -> dict:
# #     """
# #     Detects if user wants short/long, bullet points, step-by-step, examples, etc.
# #     Returns a dict of preferences.
# #     """
# #     instructions = {
# #         "concise": False,
# #         "detailed": False,
# #         "bullet_points": False,
# #         "step_by_step": False,
# #         "examples": False
# #     }

# #     lower = prompt.lower()
# #     if "short" in lower or "concise" in lower or "brief" in lower:
# #         instructions["concise"] = True
# #     if "long" in lower or "detailed" in lower or "elaborate" in lower:
# #         instructions["detailed"] = True
# #     if "bullet" in lower or "points" in lower:
# #         instructions["bullet_points"] = True
# #     if "step" in lower or "step by step" in lower:
# #         instructions["step_by_step"] = True
# #     if "example" in lower or "examples" in lower:
# #         instructions["examples"] = True

# #     return instructions

# # # ---------------------------
# # # 1️⃣ Adaptive prompt builder
# # # ---------------------------
# # def adaptive_prompt(user_prompt: str, base_instruction: str = "") -> str:
# #     """
# #     Build prompt dynamically based on detected user instructions.
# #     """
# #     instructions = detect_user_instructions(user_prompt)
    
# #     extra = []
# #     if instructions["concise"]:
# #         extra.append("Provide a brief, to-the-point answer.")
# #     if instructions["detailed"]:
# #         extra.append("Explain in detail with structured paragraphs.")
# #     if instructions["bullet_points"]:
# #         extra.append("Use bullet points for clarity.")
# #     if instructions["step_by_step"]:
# #         extra.append("Explain step by step.")
# #     if instructions["examples"]:
# #         extra.append("Provide examples where appropriate.")
    
# #     filled_prompt = (
# #         f"You are an expert academic assistant.\n"
# #         f"{base_instruction}\n"
# #         f"{' '.join(extra) if extra else 'Answer in a clear, standard style.'}\n\n"
# #         f"User Prompt: {user_prompt}\nAnswer:"
# #     )
# #     return filled_prompt

# # # ---------------------------
# # # 2️⃣ Summarize Text
# # # ---------------------------
# # def summarize_text(text: str) -> str:
# #     prompt_text = adaptive_prompt(
# #         text,
# #         base_instruction=(
# #             "Summarize complex scholarly material clearly, capturing objectives, "
# #             "key findings, technical terms, and logical flow. Avoid repetition or personal opinion."
# #         )
# #     )
# #     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
# #     chain = prompt | llm | parser
# #     try:
# #         return chain.invoke({"prompt": prompt_text})
# #     except Exception as e:
# #         return f"Error generating summary: {e}"

# # # ---------------------------
# # # 3️⃣ Summarize PDF
# # # ---------------------------
# # def summarize_pdf(text: str) -> str:
# #     prompt_text = adaptive_prompt(
# #         text,
# #         base_instruction=(
# #             "Summarize the PDF content capturing objectives, methods, results, "
# #             "key findings, and conclusions. Preserve technical terms and maintain formal tone."
# #         )
# #     )
# #     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
# #     chain = prompt | llm | parser
# #     try:
# #         return chain.invoke({"prompt": prompt_text})
# #     except Exception as e:
# #         return f"Error summarizing PDF: {e}"

# # # ---------------------------
# # # 4️⃣ Enhance Prompt
# # # ---------------------------
# # def enhance_prompt(prompt_text: str) -> str:
# #     prompt_text = adaptive_prompt(
# #         prompt_text,
# #         base_instruction=(
# #             "Rewrite the user's prompt for clarity, structure, and specificity. "
# #             "Add instructions for better AI responses if missing."
# #         )
# #     )
# #     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
# #     chain = prompt | llm | parser
# #     try:
# #         return chain.invoke({"prompt": prompt_text})
# #     except Exception as e:
# #         return f"Error enhancing prompt: {e}"

# # # ---------------------------
# # # 5️⃣ Answer Question (Multi-PDF)
# # # ---------------------------
# # def answer_question(pdf_texts: list, question: str, conversation_history: str) -> str:
# #     combined_texts = ""
# #     for i, text in enumerate(pdf_texts, 1):
# #         combined_texts += f"[PDF {i}]\n{text}\n\n"
    
# #     base_instruction = (
# #         "Use the following PDFs and conversation history to answer the user's question. "
# #         "Include bullet points for methodology or technical steps and cite PDF numbers where relevant."
# #     )
# #     prompt_text = adaptive_prompt(question, base_instruction=base_instruction)
    
# #     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
# #     chain = prompt | llm | parser
# #     try:
# #         return chain.invoke({"prompt": prompt_text})
# #     except Exception as e:
# #         return f"Error answering question: {e}"

# # # ---------------------------
# # # 6️⃣ Generate Search Queries
# # # ---------------------------
# # async def generate_search_query(text: str) -> list[str]:
# #     """
# #     Generate multiple concise search keywords/queries from user-provided text.
# #     """
# #     base_instruction = (
# #         "Generate 3-5 concise search queries focusing on technical keywords, concepts, "
# #         "and relevant terminology. Return as a comma-separated list."
# #     )
# #     prompt_text = adaptive_prompt(text, base_instruction=base_instruction)
    
# #     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
# #     chain = prompt | llm | parser
# #     try:
# #         result = chain.invoke({"prompt": prompt_text})
# #         queries = [q.strip() for q in result.split(",") if q.strip()]
# #         return queries
# #     except Exception as e:
# #         print(f"Error generating search queries: {e}")
# #         return []


# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv
# import asyncio  # kept in case you extend with async calls later

# load_dotenv()

# # ------------------------------------------------------------------
# # Shared Groq LLM instance
# # Requires: GROQ_API_KEY in your .env (or environment variables)
# # ------------------------------------------------------------------
# llm = ChatGroq(
#     model="llama3-8b-8192",  # You can change to any Groq-supported model
#     temperature=0.3,
# )
# parser = StrOutputParser()


# # ---------------------------
# # 0️⃣ Utility: Detect user instructions
# # ---------------------------
# def detect_user_instructions(prompt: str) -> dict:
#     """
#     Detects if user wants short/long, bullet points, step-by-step, examples, etc.
#     Returns a dict of preferences.
#     """
#     instructions = {
#         "concise": False,
#         "detailed": False,
#         "bullet_points": False,
#         "step_by_step": False,
#         "examples": False,
#     }

#     lower = prompt.lower()
#     if "short" in lower or "concise" in lower or "brief" in lower:
#         instructions["concise"] = True
#     if "long" in lower or "detailed" in lower or "elaborate" in lower:
#         instructions["detailed"] = True
#     if "bullet" in lower or "points" in lower:
#         instructions["bullet_points"] = True
#     if "step" in lower or "step by step" in lower:
#         instructions["step_by_step"] = True
#     if "example" in lower or "examples" in lower:
#         instructions["examples"] = True

#     return instructions


# # ---------------------------
# # 1️⃣ Adaptive prompt builder
# # ---------------------------
# def adaptive_prompt(user_prompt: str, base_instruction: str = "") -> str:
#     """
#     Build prompt dynamically based on detected user instructions.
#     """
#     instructions = detect_user_instructions(user_prompt)

#     extra = []
#     if instructions["concise"]:
#         extra.append("Provide a brief, to-the-point answer.")
#     if instructions["detailed"]:
#         extra.append("Explain in detail with structured paragraphs.")
#     if instructions["bullet_points"]:
#         extra.append("Use bullet points for clarity.")
#     if instructions["step_by_step"]:
#         extra.append("Explain step by step.")
#     if instructions["examples"]:
#         extra.append("Provide examples where appropriate.")

#     filled_prompt = (
#         "You are an expert academic assistant.\n"
#         f"{base_instruction}\n"
#         f"{' '.join(extra) if extra else 'Answer in a clear, standard style.'}\n\n"
#         f"User Prompt: {user_prompt}\nAnswer:"
#     )
#     return filled_prompt


# # ---------------------------
# # 2️⃣ Summarize Text
# # ---------------------------
# def summarize_text(text: str) -> str:
#     prompt_text = adaptive_prompt(
#         text,
#         base_instruction=(
#             "Summarize complex scholarly material clearly, capturing objectives, "
#             "key findings, technical terms, and logical flow. Avoid repetition or personal opinion."
#         ),
#     )
#     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
#     chain = prompt | llm | parser
#     try:
#         return chain.invoke({"prompt": prompt_text})
#     except Exception as e:
#         return f"Error generating summary: {e}"


# # ---------------------------
# # 3️⃣ Summarize PDF
# # ---------------------------
# def summarize_pdf(text: str) -> str:
#     prompt_text = adaptive_prompt(
#         text,
#         base_instruction=(
#             "Summarize the PDF content capturing objectives, methods, results, "
#             "key findings, and conclusions. Preserve technical terms and maintain formal tone."
#         ),
#     )
#     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
#     chain = prompt | llm | parser
#     try:
#         return chain.invoke({"prompt": prompt_text})
#     except Exception as e:
#         return f"Error summarizing PDF: {e}"


# # ---------------------------
# # 4️⃣ Enhance Prompt
# # ---------------------------
# def enhance_prompt(prompt_text: str) -> str:
#     prompt_text = adaptive_prompt(
#         prompt_text,
#         base_instruction=(
#             "Rewrite the user's prompt for clarity, structure, and specificity. "
#             "Add instructions for better AI responses if missing."
#         ),
#     )
#     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
#     chain = prompt | llm | parser
#     try:
#         return chain.invoke({"prompt": prompt_text})
#     except Exception as e:
#         return f"Error enhancing prompt: {e}"


# # ---------------------------
# # 5️⃣ Answer Question (Multi-PDF)
# # ---------------------------
# def answer_question(pdf_texts: list, question: str, conversation_history: str) -> str:
#     """
#     Answer a question using multiple PDFs plus conversation history.
#     Signature kept identical to original implementation.
#     """
#     combined_texts = ""
#     for i, text in enumerate(pdf_texts, 1):
#         combined_texts += f"[PDF {i}]\n{text}\n\n"

#     base_instruction = (
#         "Use the following PDFs and conversation history to answer the user's question. "
#         "Include bullet points for methodology or technical steps and cite PDF numbers where relevant."
#     )

#     # Include PDFs and history explicitly in the user prompt
#     user_prompt = (
#         f"{base_instruction}\n\n"
#         f"Conversation history:\n{conversation_history}\n\n"
#         f"PDF contents:\n{combined_texts}\n\n"
#         f"Question:\n{question}"
#     )

#     prompt_text = adaptive_prompt(user_prompt, base_instruction="")

#     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
#     chain = prompt | llm | parser
#     try:
#         return chain.invoke({"prompt": prompt_text})
#     except Exception as e:
#         return f"Error answering question: {e}"


# # ---------------------------
# # 6️⃣ Generate Search Queries
# # ---------------------------
# async def generate_search_query(text: str) -> list[str]:
#     """
#     Generate multiple concise search keywords/queries from user-provided text.
#     Note: This is an async function but uses a synchronous invoke under the hood,
#     matching the original design.
#     """
#     base_instruction = (
#         "Generate 3-5 concise search queries focusing on technical keywords, concepts, "
#         "and relevant terminology. Return as a comma-separated list."
#     )
#     prompt_text = adaptive_prompt(text, base_instruction=base_instruction)

#     prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
#     chain = prompt | llm | parser

#     try:
#         # Synchronous call inside async function (same pattern as original code)
#         result = chain.invoke({"prompt": prompt_text})
#         queries = [q.strip() for q in result.split(",") if q.strip()]
#         return queries
#     except Exception as e:
#         print(f"Error generating search queries: {e}")
#         return []


import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ------------------------------------------------------------------
# Groq client (no LangChain)
# ------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Please add it to Backend/.env."
    )

client = Groq(api_key=GROQ_API_KEY, timeout=30.0)

def _call_groq(prompt: str, model: str = "llama-3.1-8b-instant") -> str:
# def _call_groq(prompt: str, model: str = "llama-3.3-8b-instant") -> str:
# def _call_groq(prompt: str, model: str = "llama3-8b-8192") -> str:
    """
    Helper function to call Groq chat completion.
    """
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=1024,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling Groq: {e}"


# ---------------------------
# 0️⃣ Utility: Detect user instructions
# ---------------------------
def detect_user_instructions(prompt: str) -> dict:
    """
    Detects if user wants short/long, bullet points, step-by-step, examples, etc.
    Returns a dict of preferences.
    """
    instructions = {
        "concise": False,
        "detailed": False,
        "bullet_points": False,
        "step_by_step": False,
        "examples": False,
    }

    lower = prompt.lower()
    if "short" in lower or "concise" in lower or "brief" in lower:
        instructions["concise"] = True
    if "long" in lower or "detailed" in lower or "elaborate" in lower:
        instructions["detailed"] = True
    if "bullet" in lower or "points" in lower:
        instructions["bullet_points"] = True
    if "step" in lower or "step by step" in lower:
        instructions["step_by_step"] = True
    if "example" in lower or "examples" in lower:
        instructions["examples"] = True

    return instructions


# ---------------------------
# 1️⃣ Adaptive prompt builder
# ---------------------------
def adaptive_prompt(user_prompt: str, base_instruction: str = "") -> str:
    """
    Build prompt dynamically based on detected user instructions.
    """
    instructions = detect_user_instructions(user_prompt)

    extra = []
    if instructions["concise"]:
        extra.append("Provide a brief, to-the-point answer.")
    if instructions["detailed"]:
        extra.append("Explain in detail with structured paragraphs.")
    if instructions["bullet_points"]:
        extra.append("Use bullet points for clarity.")
    if instructions["step_by_step"]:
        extra.append("Explain step by step.")
    if instructions["examples"]:
        extra.append("Provide examples where appropriate.")

    filled_prompt = (
        "You are an expert academic assistant.\n"
        f"{base_instruction}\n"
        f"{' '.join(extra) if extra else 'Answer in a clear, standard style.'}\n\n"
        f"User Prompt: {user_prompt}\nAnswer:"
    )
    return filled_prompt


# ---------------------------
# 2️⃣ Summarize Text
# ---------------------------
def summarize_text(text: str) -> str:
    prompt_text = adaptive_prompt(
        text,
        base_instruction=(
            "Summarize complex scholarly material clearly, capturing objectives, "
            "key findings, technical terms, and logical flow. Avoid repetition or personal opinion."
        ),
    )
    try:
        return _call_groq(prompt_text)
    except Exception as e:
        return f"Error generating summary: {e}"


# ---------------------------
# 3️⃣ Summarize PDF
# ---------------------------
def summarize_pdf(text: str) -> str:
    prompt_text = adaptive_prompt(
        text,
        base_instruction=(
            "Summarize the PDF content capturing objectives, methods, results, "
            "key findings, and conclusions. Preserve technical terms and maintain formal tone."
        ),
    )
    try:
        return _call_groq(prompt_text)
    except Exception as e:
        return f"Error summarizing PDF: {e}"


# ---------------------------
# 4️⃣ Enhance Prompt
# ---------------------------
def enhance_prompt(prompt_text: str) -> str:
    prompt_text = adaptive_prompt(
        prompt_text,
        base_instruction=(
            "Rewrite the user's prompt for clarity, structure, and specificity. "
            "Add instructions for better AI responses if missing."
        ),
    )
    try:
        return _call_groq(prompt_text)
    except Exception as e:
        return f"Error enhancing prompt: {e}"


# ---------------------------
# 5️⃣ Answer Question (Multi-PDF)
# ---------------------------
def answer_question(pdf_texts: list, question: str, conversation_history: str) -> str:
    # Limit how much text we send from each PDF to keep prompts small and fast
    max_chars_per_pdf = 4000

    combined_texts = ""
    for i, text in enumerate(pdf_texts, 1):
        snippet = (text or "")[:max_chars_per_pdf]
        combined_texts += f"[PDF {i} snippet]\n{snippet}\n\n"

    base_instruction = (
        "Use the following PDF snippets and conversation history to answer the user's question. "
        "If information seems missing, say so. "
        "Include bullet points for methodology or technical steps and cite PDF numbers where relevant."
    )

    user_prompt = (
        f"{base_instruction}\n\n"
        f"Conversation history:\n{conversation_history}\n\n"
        f"PDF contents:\n{combined_texts}\n\n"
        f"Question:\n{question}"
    )

    prompt_text = adaptive_prompt(user_prompt, base_instruction="")

    try:
        return _call_groq(prompt_text)
    except Exception as e:
        return f"Error answering question: {e}"

# ---------------------------
# 6️⃣ Generate Search Queries
# ---------------------------
async def generate_search_query(text: str) -> list[str]:
    """
    Generate multiple concise search keywords/queries from user-provided text.
    Async to keep the same signature used elsewhere.
    """
    base_instruction = (
        "Generate 3-5 concise search queries focusing on technical keywords, concepts, "
        "and relevant terminology. Return as a comma-separated list."
    )
    prompt_text = adaptive_prompt(text, base_instruction=base_instruction)

    try:
        result = _call_groq(prompt_text)
        queries = [q.strip() for q in result.split(",") if q.strip()]
        return queries
    except Exception as e:
        print(f"Error generating search queries: {e}")
        return []