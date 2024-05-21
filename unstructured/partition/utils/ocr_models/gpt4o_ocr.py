from __future__ import annotations

import base64
import json
from io import BytesIO
from typing import TYPE_CHECKING

from openai import OpenAI
import os

from unstructured.documents.elements import ElementType

from unstructured.partition.utils.constants import Source
from unstructured.partition.utils.ocr_models.ocr_interface import OCRAgent
from unstructured_inference.inference.elements import Rectangle, TextRegion

from unstructured.partition.pdf_image.inference_utils import (
    build_layout_element,
)

if TYPE_CHECKING:
    from PIL import Image as PILImage
    from unstructured_inference.inference.layoutelement import LayoutElement


class OCRAgentGPT4O(OCRAgent):
    """OCR service implementation for OpenAI gpt4o API."""

    def __init__(self) -> None:
        self.model = "gpt-4o"
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def is_text_sorted(self) -> bool:
        return True

    def get_text_from_image(self, image: PILImage.Image, ocr_languages: str = "eng") -> str:
        with BytesIO() as buffer:
            image.save(buffer, format="PNG")
            encoded_image = base64.b64encode(buffer.getvalue())

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that performs OCR tasks. Transcribe the following image only with the text that appears in the image.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"image": encoded_image},
                        ],
                    },
                ],
                temperature=0.0,
            )

        return (
            "" if not response.choices[0].message.content else response.choices[0].message.content
        )

        # response = self.client.document_text_detection(image=Image(content=buffer.getvalue()))
        # document = response.full_text_annotation
        # assert isinstance(document, TextAnnotation)
        # return document.text

    def get_layout_from_image(
        self, image: PILImage.Image, ocr_languages: str = "eng"
    ) -> list[TextRegion]:
        
        with BytesIO() as buffer:
            image.save(buffer, format="PNG")
            encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that performs OCR tasks. Transcribe the text of the following image into a list of paragraphs in a json list. The list should contain the transcription of text that appear in any direction.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"image": encoded_image},
                        ],
                    },
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )

        paragraph_list = (
            [] if not response.choices[0].message.content else json.loads(response.choices[0].message.content)
        )
        

        #with open("gpt4o_response.content.json") as f:
        #    paragraph_list = json.load(f)

        return [
            TextRegion(
                bbox=Rectangle(x1=1, y1=1, x2=2, y2=2),
                text=paragraph,
                source=Source.OCR_GPT4O,
            )
            for paragraph in paragraph_list["paragraphs"]
        ]

    def get_layout_elements_from_image(
        self, image: PILImage.Image, ocr_languages: str = "eng"
    ) -> list[LayoutElement]:

        ocr_regions = self.get_layout_from_image(
            image,
            ocr_languages=ocr_languages,
        )

        return [
            build_layout_element(
                bbox=r.bbox,
                text=r.text,
                source=r.source,
                element_type=ElementType.UNCATEGORIZED_TEXT,
            )
            for r in ocr_regions
        ]