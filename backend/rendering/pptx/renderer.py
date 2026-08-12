from copy import deepcopy
from pathlib import Path
from typing import Any, cast

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.presentation import Presentation as PresentationType
from pptx.shapes.picture import Picture
from pptx.shapes.shapetree import SlideShapes

from backend.rendering.pptx.models import (
    SemanticColor,
    TextRenderResult,
)

SEMANTIC_COLORS = {
    SemanticColor.PROBLEM_HIGH: RGBColor(
        255,
        0,
        0,
    ),
    SemanticColor.PROBLEM_MEDIUM: RGBColor(
        237,
        112,
        20,
    ),
    SemanticColor.POSITIVE: RGBColor(
        112,
        173,
        71,
    ),
    SemanticColor.WARNING: RGBColor(
        255,
        192,
        0,
    ),
    SemanticColor.NEUTRAL: RGBColor(
        31,
        78,
        121,
    ),
}


class PowerPointRenderer:
    def __init__(
        self,
        template_path: Path,
    ) -> None:
        self._presentation = Presentation(str(template_path))

    @property
    def presentation(
        self,
    ) -> PresentationType:
        return self._presentation

    def find_shape(
        self,
        shape_name: str,
    ):
        for slide in self._presentation.slides:
            for shape in slide.shapes:
                if shape.name == shape_name:
                    return shape

        raise KeyError(f"Shape not found: {shape_name}")

    def set_text_preserving_style(
        self,
        shape_name: str,
        value: str,
        *,
        max_characters: int | None = None,
    ) -> TextRenderResult:
        shape = self.find_shape(shape_name)

        if not shape.has_text_frame:
            raise TypeError(f"Shape {shape_name} has no text frame")

        text_frame = shape.text_frame

        if not text_frame.paragraphs:
            raise ValueError(f"Shape {shape_name} contains no paragraph")

        paragraph = text_frame.paragraphs[0]

        if not paragraph.runs:
            raise ValueError(
                f"Shape {shape_name} has no template run. "
                "Editable template text must contain "
                "at least one preformatted run."
            )

        first_run = paragraph.runs[0]

        # Critical rule:
        # modify only the text contained by the existing run.
        # Do not recreate the run and do not assign any font
        # property, so PowerPoint inheritance remains intact.
        first_run.text = value

        # Remove residual template text from any additional runs
        # without deleting their XML or formatting.
        for extra_run in paragraph.runs[1:]:
            extra_run.text = ""

        # Remove residual text from additional paragraphs while
        # preserving their paragraph/run formatting structures.
        for extra_paragraph in text_frame.paragraphs[1:]:
            for extra_run in extra_paragraph.runs:
                extra_run.text = ""

        too_long = max_characters is not None and len(value) > max_characters

        return TextRenderResult(
            shape_name=shape_name,
            text=value,
            estimated_too_long=too_long,
        )

    def set_shape_border_color(
        self,
        shape_name: str,
        semantic_color: SemanticColor,
    ) -> None:
        shape = self.find_shape(shape_name)

        shape.line.color.rgb = SEMANTIC_COLORS[semantic_color]

    def set_shape_fill_color(
        self,
        shape_name: str,
        semantic_color: SemanticColor,
    ) -> None:
        shape = self.find_shape(shape_name)

        shape.fill.solid()
        shape.fill.fore_color.rgb = SEMANTIC_COLORS[semantic_color]

    def set_table_cell_text(
        self,
        shape_name: str,
        row: int,
        column: int,
        value: str,
    ) -> None:
        shape = self.find_shape(shape_name)

        if not shape.has_table:
            raise TypeError(f"Shape {shape_name} " "is not a table")

        table = shape.table

        cell = table.cell(
            row,
            column,
        )

        text_frame = cell.text_frame

        if not text_frame.paragraphs:
            paragraph = text_frame.add_paragraph()
        else:
            paragraph = text_frame.paragraphs[0]

        if not paragraph.runs:
            run = paragraph.add_run()
            run.text = value
            return

        first_run = paragraph.runs[0]

        first_run.text = value

        for extra_run in list(paragraph.runs[1:]):
            extra_run.text = ""

    def replace_picture_by_recreation(
        self,
        shape_name: str,
        image_path: Path,
    ) -> None:
        shape = self.find_shape(shape_name)

        if shape.shape_type != MSO_SHAPE_TYPE.PICTURE:
            raise TypeError(f"Shape {shape_name} is not a picture")

        picture = cast(
            Picture,
            shape,
        )

        left = picture.left
        top = picture.top
        width = picture.width
        height = picture.height

        old_element = picture._element

        xml_parent = old_element.getparent()

        if xml_parent is None:
            raise RuntimeError(f"Shape {shape_name} has no XML parent")

        old_index = xml_parent.index(old_element)

        shapes = cast(
            SlideShapes,
            picture._parent,
        )

        new_picture = shapes.add_picture(
            str(image_path),
            left,
            top,
            width,
            height,
        )

        new_picture.name = shape_name

        new_element = new_picture._element

        # add_picture() inserts the new element at
        # the end of the shape tree. Move it to the
        # exact Z-order position of the old picture.
        xml_parent.remove(new_element)

        xml_parent.insert(
            old_index,
            new_element,
        )

        xml_parent.remove(old_element)

        new_geometry = (
            new_picture.left,
            new_picture.top,
            new_picture.width,
            new_picture.height,
        )

        original_geometry = (
            left,
            top,
            width,
            height,
        )

        if new_geometry != original_geometry:
            raise RuntimeError(
                "Picture geometry changed during " f"recreation: {shape_name}"
            )

    def replace_picture(
        self,
        shape_name: str,
        image_path: Path,
        *,
        crop_mode: str = "cover",
    ) -> None:
        shape = self.find_shape(shape_name)

        if shape.shape_type != MSO_SHAPE_TYPE.PICTURE:
            raise TypeError(f"Shape {shape_name} is not a picture")

        picture = cast(
            Picture,
            shape,
        )

        original_geometry = (
            picture.left,
            picture.top,
            picture.width,
            picture.height,
        )

        slide_part = cast(
            Any,
            picture.part,
        )

        _, relationship_id = slide_part.get_or_add_image_part(str(image_path))

        blip_fill = cast(
            Any,
            picture._pic.blipFill,
        )

        blip = blip_fill.blip

        if blip is None:
            raise ValueError(f"Picture {shape_name} has no blip")

        blip.rEmbed = relationship_id

        if crop_mode == "cover":
            self._apply_cover_crop(
                picture,
                image_path,
            )
        elif crop_mode == "stretch":
            picture.crop_left = 0
            picture.crop_right = 0
            picture.crop_top = 0
            picture.crop_bottom = 0
        else:
            raise ValueError(f"Unsupported crop mode: {crop_mode}")

        current_geometry = (
            picture.left,
            picture.top,
            picture.width,
            picture.height,
        )

        if current_geometry != original_geometry:
            raise RuntimeError(
                "Picture geometry changed during " f"replacement: {shape_name}"
            )

    def _apply_cover_crop(
        self,
        picture: Picture,
        image_path: Path,
    ) -> None:
        with Image.open(image_path) as image:
            image_width, image_height = image.size

        if (
            image_width <= 0
            or image_height <= 0
            or picture.width <= 0
            or picture.height <= 0
        ):
            raise ValueError("Invalid image or picture dimensions")

        image_ratio = image_width / image_height

        frame_ratio = picture.width / picture.height

        picture.crop_left = 0
        picture.crop_right = 0
        picture.crop_top = 0
        picture.crop_bottom = 0

        if image_ratio > frame_ratio:
            visible_fraction = frame_ratio / image_ratio

            crop = (1 - visible_fraction) / 2

            picture.crop_left = crop
            picture.crop_right = crop

        elif image_ratio < frame_ratio:
            visible_fraction = image_ratio / frame_ratio

            crop = (1 - visible_fraction) / 2

            picture.crop_top = crop
            picture.crop_bottom = crop

    def set_paragraph_text_preserving_style(
        self,
        shape_name: str,
        paragraph_index: int,
        text: str,
    ) -> None:
        shape = self.find_shape(shape_name)

        if not shape.has_text_frame:
            raise ValueError(f"{shape_name} has no text frame")

        paragraphs = shape.text_frame.paragraphs

        if paragraph_index >= len(paragraphs):
            raise IndexError(
                "Paragraph index out of range: " f"{shape_name}[{paragraph_index}]"
            )

        paragraph = paragraphs[paragraph_index]

        runs = paragraph.runs

        if not runs:
            paragraph.text = text
            return

        first_run = runs[0]

        first_run.text = text

        for run in runs[1:]:
            run.text = ""

    def set_keyword_detail_preserving_style(
        self,
        shape_name: str,
        keyword: str,
        detail: str,
    ) -> None:
        shape = self.find_shape(shape_name)

        if not shape.has_text_frame:
            raise ValueError(f"{shape_name} has no text frame")

        paragraph = shape.text_frame.paragraphs[0]

        runs = list(paragraph.runs)

        if not runs:
            raise ValueError(f"{shape_name} has no template runs")

        template_bold_run = next(
            (run for run in runs if run.font.bold is True),
            runs[0],
        )

        template_regular_run = next(
            (run for run in runs if run.font.bold is not True),
            None,
        )

        bold_rpr = (
            deepcopy(template_bold_run._r.rPr)
            if template_bold_run._r.rPr is not None
            else None
        )

        regular_rpr = (
            deepcopy(template_regular_run._r.rPr)
            if (
                template_regular_run is not None
                and template_regular_run._r.rPr is not None
            )
            else None
        )

        output_keyword_run = runs[0]

        if len(runs) >= 2:
            output_detail_run = runs[1]
        else:
            output_detail_run = paragraph.add_run()

        def apply_rpr(
            run,
            rpr,
        ) -> None:
            current_rpr = run._r.rPr

            if current_rpr is not None:
                run._r.remove(current_rpr)

            if rpr is not None:
                run._r.insert(
                    0,
                    deepcopy(rpr),
                )

        apply_rpr(
            output_keyword_run,
            bold_rpr,
        )

        if regular_rpr is not None:
            apply_rpr(
                output_detail_run,
                regular_rpr,
            )
        else:
            apply_rpr(
                output_detail_run,
                bold_rpr,
            )

            output_detail_run.font.bold = False

        output_keyword_run.text = keyword

        output_detail_run.text = f" {detail}" if detail else ""

        for run in list(paragraph.runs)[2:]:
            run.text = ""

    def set_impact_statement_preserving_style(
        self,
        shape_name: str,
        value: str,
    ) -> None:
        shape = self.find_shape(shape_name)

        if not shape.has_text_frame:
            raise ValueError(f"{shape_name} has no text frame")

        text_frame = shape.text_frame

        words = value.strip().split()

        if not words:
            rendered = ""
        elif len(words) == 1:
            rendered = words[0]
        elif len(words) == 2:
            rendered = f"{words[0]}\n" f"{words[1]}"
        else:
            best_split = 1
            best_difference = None

            for index in range(
                1,
                len(words),
            ):
                first = " ".join(words[:index])
                second = " ".join(words[index:])

                difference = abs(len(first) - len(second))

                if best_difference is None or difference < best_difference:
                    best_difference = difference
                    best_split = index

            rendered = (
                " ".join(words[:best_split]) + "\n" + " ".join(words[best_split:])
            )

        paragraphs = text_frame.paragraphs

        if not paragraphs:
            raise ValueError(f"{shape_name} contains no paragraph")

        first_paragraph = paragraphs[0]

        if not first_paragraph.runs:
            raise ValueError(f"{shape_name} has no template run")

        first_run = first_paragraph.runs[0]

        first_run.text = rendered

        for run in first_paragraph.runs[1:]:
            run.text = ""

        for paragraph in paragraphs[1:]:
            for run in paragraph.runs:
                run.text = ""

        text_frame.auto_size = MSO_AUTO_SIZE.NONE

        text_frame.word_wrap = False

    def lock_text_box_geometry(
        self,
        shape_name: str,
        *,
        word_wrap: bool = True,
    ) -> None:
        shape = self.find_shape(shape_name)

        if not shape.has_text_frame:
            raise ValueError(f"{shape_name} has no text frame")

        text_frame = shape.text_frame

        text_frame.auto_size = MSO_AUTO_SIZE.NONE

        text_frame.word_wrap = word_wrap

    def replace_shape_with_picture(
        self,
        shape_name: str,
        image_path: Path,
    ) -> None:
        shape = self.find_shape(shape_name)

        left = shape.left
        top = shape.top
        width = shape.width
        height = shape.height

        old_element = shape._element

        xml_parent = old_element.getparent()

        if xml_parent is None:
            raise RuntimeError(f"{shape_name} has no XML parent")

        old_index = xml_parent.index(old_element)

        shapes = cast(
            SlideShapes,
            shape._parent,
        )

        new_picture = shapes.add_picture(
            str(image_path),
            left,
            top,
            width,
            height,
        )

        new_picture.name = shape_name

        new_element = new_picture._element

        xml_parent.remove(new_element)

        xml_parent.insert(
            old_index,
            new_element,
        )

        xml_parent.remove(old_element)

    def remove_shape(
        self,
        shape_name: str,
    ) -> None:
        shape = self.find_shape(shape_name)

        element = shape._element

        parent = element.getparent()

        if parent is None:
            raise RuntimeError(f"{shape_name} has no XML parent")

        parent.remove(element)

    def save(
        self,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._presentation.save(str(output_path))
