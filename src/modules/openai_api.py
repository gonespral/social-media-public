"""
OpenAI API module
"""

import os
import requests
import uuid
import logging

import openai

# Enable logging
logger = logging.getLogger(__name__)


def completion(content: str or list,
               api_key: str,
               role: str or list = "user",
               temperature: float = 1,
               model: str = "gpt-4"
               ) -> str:
    """
    Completion endpoint using ChatCompletion
    :param content: Content of the message
    :param api_key: Dictionary of api keys
    :param role: Role of the message
    :param temperature: Temperature setting
    :param model: Model to use
    :return: Completion
    """

    openai.api_key = api_key

    if isinstance(content, list) and isinstance(role, list):
        messages = []
        for c, r in zip(content, role):
            messages.append({"role": role, "content": content})
    elif isinstance(content, str) and isinstance(role, str):
        messages = [{"role": role, "content": content}]
    else:
        raise TypeError("Content and role must be of the same type")

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    )

    return response.choices[0].message.content


def image(prompt: str,
          api_key: str,
          n: int = 1,
          size: str = "512x512",
          output_path: str = "."
          ) -> str:
    """
    Image endpoint
    :param prompt: Prompt for image
    :param api_key: Dictionary of api keys
    :param n: Number of images to generate (1-10)
    :param size: Size of image (one of 256x256, 512x512, 1024x1024)
    :param output_path: Path to save image
    :return: Path to image
    """

    openai.api_key = api_key

    response = openai.Image.create(
        prompt=prompt,
        n=n,
        size=size,
        response_format="url"
    )

    url = response.data[0].url
    filename = f"{uuid.uuid4()}.png"
    path = os.path.join(output_path, filename)

    # Download image from url and save to output_path
    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)

    return path
