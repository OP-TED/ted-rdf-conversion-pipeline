#TED Semantic Web Services

## Developer documentation

If you contribute to this project please refer to the following project documentation:
* [GitHub pages with the enterprise architecture (in development)](https://meaningfy-ws.github.io/ted-sws/ted-sws/index.html)
* [Enterprise architecture model file (in development)](https://drive.google.com/file/d/1YB2dPYe9E9bAR2peVraQaUANS-hXetms/view?usp=sharing)
* [Meaningfy google Drive of the project (restricted)](https://drive.google.com/drive/folders/1wfWYDAtcaJrYTuB14VzTixr1mJUkCHYl?usp=sharing)

## Installation
### Installation of ted-sws package within external projects using terminal
#### 1. Using the package manager pip
1. Go to the root folder of the project
2. Use the package manager pip to install ted-sws package
```bash
pip install git+https://github.com/meaningfy-ws/ted-sws@main#egg=ted-sws
```
#### 2. Using the Makefile target
1. Go to the root folder of the project
2. Add ted-sws package "git+https://github.com/meaningfy-ws/ted-sws@main#egg=ted-sws" to the "requirements.txt" file
3. Add "setup" target to the Makefile
```bash
setup: install
	# Additional post-installation tasks/commands

install:
	@ pip install --upgrade pip
	# To make a full ted-sws package installation, including all its dependencies:
	@ pip install --upgrade --force-reinstall -r requirements.txt
	# To upgrade only ted-sws package (faster), without upgrading all the dependencies use the line below
	# (this command should be used only after a full installation, instead of the full installtion command):
	# @ pip install --upgrade --force-reinstall --no-deps -r requirements.txt
```
4. Run:
```bash
make setup
```

## Usage
### CLI tools (commands/console-scripts) for notice mapping suite manipulation

Using MAPPING_SUITE_ID argument should be enough for general purpose.

#### CMD: normalisation_resource_generator
Generates all resources files needed for notice mapping suite transformation.

Use:
```bash
normalisation_resource_generator --help
```
to get the Usage Help:
```bash
Usage: normalisation_resource_generator [OPTIONS] [MAPPING_SUITE_ID]

Options:
  -i, --opt-queries-folder TEXT               Use to overwrite default INPUT generator
  -o, --opt-output-folder TEXT                Use to overwrite default OUTPUT generator
  -m, --opt-mappings-path TEXT
  --help                                      Show this message and exit.
```

#### CMD: metadata_generator
Generates metadata.json file from Conceptual Mappings file data.

Use:
```bash
metadata_generator --help
```
to get the Usage Help:
```bash
Usage: metadata_generator [OPTIONS] [MAPPING_SUITE_ID]

  Generates Metadata from Conceptual Mappings.

Options:
  -i, --opt-conceptual-mappings-file TEXT     Use to overwrite default INPUT generator
  -o, --opt-output-metadata-file TEXT         Use to overwrite default OUTPUT generator
  -m, --opt-mappings-path TEXT
  --help                                      Show this message and exit.
```

#### CMD: yarrrml2rml_converter
Converts YARRRML data to RML data.

Use:
```bash
yarrrml2rml_converter --help
```
to get the Usage Help:
```bash
Usage: yarrrml2rml_converter [OPTIONS] [MAPPING_SUITE_ID] [RML_OUTPUT_FILE_NAME]

  Converts YARRRML to RML. Skip RML_OUTPUT_FILE_NAME to use the default name.

Options:
  -i, --opt-yarrrml-input-file TEXT           Use to overwrite default INPUT generator
  -o, --opt-rml-output-file TEXT              Use to overwrite default OUTPUT generator
  -m, --opt-mappings-path TEXT
  --help                                      Show this message and exit.
```

#### CMD: sparql_generator
Generates SPARQL queries from Conceptual Mappings file data.

Use:
```bash
sparql_generator --help
```
to get the Usage Help:
```bash
Usage: sparql_generator [OPTIONS] [MAPPING_SUITE_ID]

  Generates SPARQL queries from Conceptual Mappings.

Options:
  -i, --opt-conceptual-mappings-file TEXT         Use to overwrite default INPUT generator
  -o, --opt-output-sparql-queries-folder TEXT     Use to overwrite default OUTPUT generator
  -rq-name, --opt-rq-name TEXT
  -m, --opt-mappings-path TEXT
  --help                                          Show this message and exit.
```

#### CMD: transformer
Transforms the Test Mapping Suites.

Use:
```bash
transformer --help
```
to get the Usage Help:
```bash
Usage: transformer [OPTIONS] [MAPPING_SUITE_ID] [SERIALIZATION_FORMAT]

  Transforms the Test Mapping Suites (identified by mapping-suite-id). If no
  mapping-suite-id is provided, all mapping suites from mappings directory
  will be processed.

Options:
  --opt-mapping-suite-id TEXT                 MappingSuite ID to be processed (leave empty
                                              to process all Mapping Suites).
  --opt-serialization-format TEXT             Serialization format (turtle (default),
                                              nquads, trig, trix, jsonld, hdt).
  --opt-mappings-path TEXT
  --opt-output-path TEXT
  --help                                      Show this message and exit.
```

#### CMD: mapping_suite_processor
Processes Mapping Suite (identified by mapping-suite-id).

By default, successively runs the following commands:
```bash
- normalisation_resource_generator
- metadata_generator
- yarrrml2rml_converter
- sparql_generator
- transformer
```

Use:
```bash
mapping_suite_processor --help
```
to get the Usage Help:
```bash
Usage: mapping_suite_processor [OPTIONS] MAPPING_SUITE_ID

  Processes Mapping Suite (identified by mapping-suite-id): -
  normalisation_resource_generator - metadata_generator -
  yarrrml2rml_converter - sparql_generator - transformer

Options:
  -c, --opt-commands [normalisation_resource_generator|metadata_generator|yarrrml2rml_converter|sparql_generator|transformer]
  -m, --opt-mappings-path TEXT
  --help                                      Show this message and exit.
```
Use:
```bash
mapping_suite_processor -c COMMAND1 -c COMMAND2 ...
```
to set custom commands (order) to be executed

## Contributions

## Licence