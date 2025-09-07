import json
from typing import List, Any
import openai
from chatbot.domain.ports import GenerativeAIProvider
from chatbot.domain.models import ChatMessage


class OpenAIProvider(GenerativeAIProvider):
    """Implementation of the Generative AI Provider using the OpenAI API."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str = None) -> None:
        """
        Initializes the OpenAI provider.

        Args:
            model (str): The name of the OpenAI model to use. Defaults to "gpt-4o-mini".
            api_key (str): The OpenAI API key. If not provided, it will be read from the OPENAI_API_KEY environment variable.
        """
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)
        print(f"OpenAIProvider initialized with model: {self.model}")

    def _safely_extract_llm_value(self, value: Any) -> str:
        """
        Helper function to safely extract values from LLM responses.

        Args:
            value (Any): The value to extract.

        Returns:
            str: The extracted string value, or "Unknown" if extraction fails.
        """
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and 'value' in value and isinstance(value['value'], str):
            return value['value']
        if isinstance(value, (int, float, bool)):
            return str(value)
        return "Unknown"

    def classify_topic_and_stance(self, message: str) -> dict:
        """
        Uses OpenAI to classify the topic and stance from a given message.

        Args:
            message (str): The user's message to classify.

        Returns:
            dict: A dictionary containing "topic" and "stance" keys.
        """
        system_prompt = """
        You are an expert topic classifier. Analyze the user's message and identify the main debate topic
        (e.g., 'Moon Landing', 'Vaccines', 'Climate Change', 'Flat Earth') and the user's stance
        (e.g., 'pro-vaccine', 'anti-moon-landing').
        Respond ONLY with a valid JSON object with keys "topic" and "stance". Do not add any other text.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            content = json.loads(response.choices[0].message.content)

            topic = self._safely_extract_llm_value(content.get("topic"))
            stance = self._safely_extract_llm_value(content.get("stance"))

            return {"topic": topic, "stance": stance}
        except (openai.APIError, json.JSONDecodeError, KeyError) as e:
            print(f"Error processing OpenAI response for classification: {e}")
            return {"topic": "General", "stance": "neutral"}

    def get_debate_response(self, topic: str, position: str, history: List[ChatMessage]) -> str:
        """
        Uses OpenAI to generate a debate response based on a given topic, position, and chat history.

        Args:
            topic (str): The current debate topic.
            position (str): The unwavering position to maintain.
            history (List[ChatMessage]): A list of previous chat messages to provide context.

        Returns:
            str: The generated counter-argument or an error message.
        """
        system_prompt = f"""
        You are a skeptical and stubborn debater. Your only goal is to find flaws and counter-arguments.
        Your current debate topic is: {topic}.
        Your unwavering, explicit position is: {position}.

        RULES:
        1. NEVER agree with the user.
        2. ALWAYS find a counter-argument, even if it's a conspiracy theory.
        3. Be critical of the user's points.
        4. Keep your responses concise, impactful, and in English.
        5. Start your response directly with your counter-argument. Do not start with phrases like "As a skeptical debater...".
        """
        messages_for_api = [{'role': 'system', 'content': system_prompt}]
        for msg in history:
            role = "assistant" if msg.role == "bot" else msg.role
            messages_for_api.append({'role': role, 'content': msg.message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages_for_api
            )
            return response.choices[0].message.content
        except openai.APIError as e:
            print(f"Error generating OpenAI response: {e}")
            return "I'm having trouble thinking of a counter-argument right now. Let's try another topic."
