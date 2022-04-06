import json
import logging
from pathlib import Path

import click
from ted_sws.core.adapters.sparql_triple_store import SPARQLTripleStore, TripleStoreABC
from ted_sws.metadata_normaliser.resources import MAPPING_FILES_PATH, QUERIES_PATH

logger = logging.getLogger(__name__)


@click.command()
@click.option('--queries-folder-path', default=QUERIES_PATH)
@click.option('--output-folder-path', default=MAPPING_FILES_PATH)
def main(queries_folder_path, output_folder_path):
    generate_mapping_files(Path(queries_folder_path), Path(output_folder_path), SPARQLTripleStore())


def generate_mapping_files(queries_folder_path: Path = QUERIES_PATH,
                           output_folder_path: Path = MAPPING_FILES_PATH,
                           triple_store: TripleStoreABC = SPARQLTripleStore()):
    """
    This method will generate a json file for each ran SPARQL query in the resources folder
    :param triple_store:
    :param queries_folder_path:
    :param output_folder_path:
    :return:
    """
    query_files_paths = list(Path(queries_folder_path).rglob("*.rq"))

    for query_file_path in query_files_paths:
        json_file_name = query_file_path.stem + ".json"
        path = output_folder_path / json_file_name
        json_content = triple_store.with_query_from_file(
            sparql_query_file_path=str(query_file_path)).fetch_tree()
        with open(path, 'w') as outfile:
            json.dump(json_content, outfile)

    logger.info(f"Mapping files were generated in {output_folder_path}")

if __name__ == '__main__':
    generate_mapping_files()
