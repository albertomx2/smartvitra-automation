from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateV2ImageBinding:
    key: str
    shape_name: str


TEMPLATE_V2_IMAGE_BINDINGS = {
    "cover_photo": TemplateV2ImageBinding(
        key="cover_photo",
        shape_name="sv_s01_cover_photo",
    ),
    "problem_photo": TemplateV2ImageBinding(
        key="problem_photo",
        shape_name="sv_s02_problem_photo",
    ),
    "generated_solution": TemplateV2ImageBinding(
        key="generated_solution",
        shape_name=("sv_s03_generated_solution_image"),
    ),
    "project_photo_1": TemplateV2ImageBinding(
        key="project_photo_1",
        shape_name="sv_s05_project_photo_1",
    ),
    "project_photo_2": TemplateV2ImageBinding(
        key="project_photo_2",
        shape_name="sv_s05_project_photo_2",
    ),
    "project_photo_3": TemplateV2ImageBinding(
        key="project_photo_3",
        shape_name="sv_s05_project_photo_3",
    ),
    "generated_result": TemplateV2ImageBinding(
        key="generated_result",
        shape_name=("sv_s07_generated_result_image"),
    ),
}
