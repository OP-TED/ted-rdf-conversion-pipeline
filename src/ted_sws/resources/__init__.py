import pathlib

RESOURCES_PATH = pathlib.Path(__file__).parent.resolve()

PREFIXES_PATH = RESOURCES_PATH / 'prefixes'
QUERIES_PATH = RESOURCES_PATH / 'queries'
SHACL_SHAPES_PATH = RESOURCES_PATH / 'shacl_shapes'
XSLT_FILES_PATH = RESOURCES_PATH / 'xslt_files'
SHACL_RESULT_QUERY_PATH = SHACL_SHAPES_PATH / 'shacl_result_query.rq'
