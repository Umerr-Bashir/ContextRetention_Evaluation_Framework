from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam
)
from openai import OpenAI, APIStatusError
from dotenv import load_dotenv
from time import perf_counter
from typing import cast, Any
import os

# Request to LLM
def llm_request(text: str, schema_val, prompt: str) -> dict[str, Any] | None:
    load_dotenv()
    client = OpenAI(
        api_key=os.getenv("API_KEY"),
        timeout=120
    )

    messages = [
        cast(
            ChatCompletionSystemMessageParam,
            cast(object, {
                "role": "system",
                "content": prompt
            })
        ),
        cast(
            ChatCompletionUserMessageParam,
            cast(object, {
                "role": "user",
                "content": text
            })
        )
    ]
    start = perf_counter()
    try:
        completion = client.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            response_format=schema_val,
            temperature=0.2
        )
        latency = perf_counter() - start

        result = completion.choices[0].message.content

        if not result:
            raise ValueError("LLM returned an empty response")

        return {
            "summary": result,
            "total_latency": latency,
            "total_input_tokens": (
                completion.usage.prompt_tokens
                if completion.usage else None
            ),
            "total_output_tokens": (
                completion.usage.completion_tokens
                if completion.usage else None
            )
        }

    except APIStatusError as e:

        print("Status:", e.status_code)

        print("Error:", e.message)

        print("Response:", e.response.text)
