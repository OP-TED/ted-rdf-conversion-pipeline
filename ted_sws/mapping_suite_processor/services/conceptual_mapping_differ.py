import json

from ted_sws.core.model.transform import ConceptualMapping
from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import mapping_suite_read_conceptual_mapping
from pathlib import Path
from deepdiff import DeepDiff
from ted_sws import config
import tempfile
from typing import List
from urllib.request import urlopen
from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME
from jinja2 import Environment, PackageLoader
from json2html import json2html
from ted_sws.core.model.transform import ConceptualMappingDiff

TEMPLATES = Environment(loader=PackageLoader("ted_sws.mapping_suite_processor.resources", "templates"))
CONCEPTUAL_MAPPINGS_DIFF_HTML_REPORT_TEMPLATE = "conceptual_mappings_diff_report.jinja2"

GITHUB_CONCEPTUAL_MAPPINGS_PATH = "{GITHUB_BASE}/raw/{GIT_BRANCH}/mappings/{MAPPING_SUITE_ID}/" + \
                                  MS_TRANSFORM_FOLDER_NAME + "/" + MS_CONCEPTUAL_MAPPING_FILE_NAME


def mapping_suite_diff_conceptual_mappings(mappings: List[ConceptualMapping]) -> dict:
    """
    This service return the difference between 2 Mapping Suite's conceptual mapping objects
    :param mappings:
    :return:
    """
    assert mappings and len(mappings) == 2
    return DeepDiff(mappings[0].dict(), mappings[1].dict(), ignore_order=True)


def mapping_suite_diff_files_conceptual_mappings(filepaths: List[Path]) -> dict:
    """
    This service return the difference between 2 Mapping Suite's conceptual mapping objects
    based on their filepaths
    :param filepaths:
    :return:
    """
    assert filepaths and len(filepaths) == 2
    return mapping_suite_diff_conceptual_mappings([
        mapping_suite_read_conceptual_mapping(filepaths[0]),
        mapping_suite_read_conceptual_mapping(filepaths[1])
    ])


def mapping_suite_diff_repo_conceptual_mappings(branch_or_tag_name: List[str], mapping_suite_id: List[str],
                                                filepath: Path = None) -> dict:
    """
    This service return the difference between 2 Mapping Suite's conceptual mapping objects
    based on their repository branch

    1) repo vs file
    2) repo vs repo

    :param github_repository_url:
    :param mapping_suite_id:
    :param branch_or_tag_name:
    :param filepath:
    :return:
    """

    assert branch_or_tag_name and len(branch_or_tag_name) > 0
    assert mapping_suite_id and len(mapping_suite_id) > 0

    git_extension = ".git"
    github_base = config.GITHUB_TED_SWS_ARTEFACTS_URL
    if github_base.endswith(git_extension):
        github_base = github_base[:-(len(git_extension))]

    url_resource = urlopen(GITHUB_CONCEPTUAL_MAPPINGS_PATH.format(
        GITHUB_BASE=github_base,
        GIT_BRANCH=branch_or_tag_name[0],
        MAPPING_SUITE_ID=mapping_suite_id[0]
    ))
    temp_file1 = tempfile.NamedTemporaryFile()
    temp_file1.write(url_resource.read())
    filepath1 = Path(temp_file1.name)

    if filepath:
        filepath2 = filepath
    else:
        if len(branch_or_tag_name) < 2:
            branch_or_tag_name.append(branch_or_tag_name[0])

        if len(mapping_suite_id) < 2:
            mapping_suite_id.append(mapping_suite_id[0])

        url_resource = urlopen(GITHUB_CONCEPTUAL_MAPPINGS_PATH.format(
            GITHUB_BASE=github_base,
            GIT_BRANCH=branch_or_tag_name[1],
            MAPPING_SUITE_ID=mapping_suite_id[1]
        ))
        temp_file2 = tempfile.NamedTemporaryFile()
        temp_file2.write(url_resource.read())
        filepath2 = Path(temp_file2.name)

    return mapping_suite_diff_files_conceptual_mappings([filepath1, filepath2])


def generate_conceptual_mappings_diff_html_report(diff: ConceptualMappingDiff):
    html_report = TEMPLATES.get_template(CONCEPTUAL_MAPPINGS_DIFF_HTML_REPORT_TEMPLATE).render({
        "metadata": json.dumps(diff.metadata, indent=2),
        "data": json2html.convert(
            json=diff.data,
            table_attributes='class="display" border="1"',
            clubbing=True
        )
    })
    return html_report
