# TED Semantic Web Services

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=meaningfy-ws_ted-sws&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=meaningfy-ws_ted-sws)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=meaningfy-ws_ted-sws&metric=bugs)](https://sonarcloud.io/summary/new_code?id=meaningfy-ws_ted-sws)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=meaningfy-ws_ted-sws&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=meaningfy-ws_ted-sws)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=meaningfy-ws_ted-sws&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=meaningfy-ws_ted-sws)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=meaningfy-ws_ted-sws&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=meaningfy-ws_ted-sws)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=meaningfy-ws_ted-sws&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=meaningfy-ws_ted-sws)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=meaningfy-ws_ted-sws&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=meaningfy-ws_ted-sws)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=meaningfy-ws_ted-sws&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=meaningfy-ws_ted-sws)

![Doc build](https://github.com/meaningfy-ws/ted-sws/actions/workflows/main.yml/badge.svg?branch=main)
![UTest build](https://github.com/meaningfy-ws/ted-sws/actions/workflows/unit-tests.yml/badge.svg?branch=main)
![E2E Test build](https://github.com/meaningfy-ws/ted-sws/actions/workflows/unit-tests-hermes.yml/badge.svg?branch=main)

## Table of contents

- [Developer documentation](#developer-documentation)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Licence](#licence)


<hr>

## Developer documentation

If you contribute to this project please refer to the following project documentation:
* [GitHub pages with the enterprise architecture (in development)](https://meaningfy-ws.github.io/ted-sws/ted-sws/index.html)
* [Enterprise architecture model file (in development)](https://drive.google.com/file/d/1YB2dPYe9E9bAR2peVraQaUANS-hXetms/view?usp=sharing)
* [Meaningfy google Drive of the project (restricted)](https://drive.google.com/drive/folders/1wfWYDAtcaJrYTuB14VzTixr1mJUkCHYl?usp=sharing)

<hr>

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

<hr>

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
  -i, --opt-queries-folder TEXT               Use to overwrite default INPUT
  -o, --opt-output-folder TEXT                Use to overwrite default OUTPUT
  -m, --opt-mappings-folder TEXT
  --help                                      Show this message and exit.
```

#### CMD: resources_injector
Injects the requested resources from Conceptual Mappings into the MappingSuite.

Use:
```bash
resources_injector --help
```
to get the Usage Help:
```bash
Usage: resources_injector [OPTIONS] [MAPPING_SUITE_ID]

  Injects the requested resources from Conceptual Mappings into the MappingSuite

Options:
  -i, --opt-conceptual-mappings-file TEXT     Use to overwrite default INPUT
  -o, --opt-output-folder TEXT                Use to overwrite default OUTPUT
  -r, --opt-resources-folder TEXT
  -m, --opt-mappings-folder TEXT
  --help                                      Show this message and exit.
```

#### CMD: rml_modules_injector
Injects the requested RML modules from Conceptual Mappings into the MappingSuite.

Use:
```bash
rml_modules_injector --help
```
to get the Usage Help:
```bash
Usage: rml_modules_injector [OPTIONS] [MAPPING_SUITE_ID]

  Injects the requested RML modules from Conceptual Mappings into the MappingSuite

Options:
  -i, --opt-conceptual-mappings-file TEXT     Use to overwrite default INPUT
  -o, --opt-output-folder TEXT                Use to overwrite default OUTPUT
  -c, --opt-clean BOOLEAN                     Use to clean the OUTPUT folder
  -r, --opt-rml-modules-folder TEXT
  -m, --opt-mappings-folder TEXT
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
  -i, --opt-conceptual-mappings-file TEXT     Use to overwrite default INPUT
  -o, --opt-output-metadata-file TEXT         Use to overwrite default OUTPUT
  -m, --opt-mappings-folder TEXT
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
  -i, --opt-yarrrml-input-file TEXT           Use to overwrite default INPUT
  -o, --opt-rml-output-file TEXT              Use to overwrite default OUTPUT
  -m, --opt-mappings-folder TEXT
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
  -i, --opt-conceptual-mappings-file TEXT         Use to overwrite default INPUT
  -o, --opt-output-sparql-queries-folder TEXT     Use to overwrite default OUTPUT
  -rq-name, --opt-rq-name TEXT
  -m, --opt-mappings-folder TEXT
  --help                                          Show this message and exit.
```

#### CMD: mapping_runner
Transforms the Test Mapping Suites.

Use:
```bash
mapping_runner --help
```
to get the Usage Help:
```bash
Usage: mapping_runner [OPTIONS] [MAPPING_SUITE_ID] [SERIALIZATION_FORMAT]

  Transforms the Test Mapping Suites (identified by mapping-suite-id). If no
  mapping-suite-id is provided, all mapping suites from mappings directory
  will be processed.

Options:
  --opt-mapping-suite-id TEXT                 MappingSuite ID to be processed (leave empty
                                              to process all Mapping Suites).
  --opt-serialization-format TEXT             Serialization format (turtle (default),
                                              nquads, trig, trix, jsonld, hdt).
  --opt-mappings-folder TEXT
  --opt-output-folder TEXT
  --help                                      Show this message and exit.
```

#### CMD: mapping_suite_processor
Processes Mapping Suite (identified by mapping-suite-id).

By default, successively runs the following commands:
```bash
- normalisation_resource_generator
- resources_injector
- metadata_generator
- yarrrml2rml_converter
- sparql_generator
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
  yarrrml2rml_converter - sparql_generator

Options:
  -c, --opt-commands [normalisation_resource_generator|resources_injector|metadata_generator|yarrrml2rml_converter|sparql_generator]
  -m, --opt-mappings-folder TEXT
  --help                                      Show this message and exit.
```
Use:
```bash
mapping_suite_processor -c COMMAND1 -c COMMAND2 ...
```
to set custom commands (order) to be executed


#### CMD: sparql_runner
Generates SPARQL Validation Reports for RDF files.

Use:
```bash
sparql_runner --help
```
to get the Usage Help:
```bash
Usage: sparql_runner [OPTIONS] [MAPPING_SUITE_ID]

  Generates Validation Reports for RDF files

Options:
  -m, --opt-mappings-folder TEXT
  --help                                      Show this message and exit.
```

#### CMD: xpath_coverage_runner
Generates Coverage Reports for Notices

Use:
```bash
xpath_coverage_runner --help
```
to get the Usage Help:
```bash
Usage: xpath_coverage_runner [OPTIONS] [MAPPING_SUITE_ID]

  Generates Coverage Reports for Notices

Options:
  -i, --opt-conceptual-mappings-file TEXT     Use to overwrite default INPUT
  -m, --opt-mappings-folder TEXT

  --help                                      Show this message and exit.
```

#### CMD: shacl_runner
Generates SHACL Validation Reports for RDF files.

Use:
```bash
shacl_runner --help
```
to get the Usage Help:
```bash
Usage: shacl_runner [OPTIONS] [MAPPING_SUITE_ID]

  Generates SHACL Validation Reports for RDF files

Options:
  -m, --opt-mappings-folder TEXT
  --help                                      Show this message and exit.
```

#### CMD: rml_report_generator
Generates RML modules report file for Mapping Suite.

Use:
```bash
rml_report_generator --help
```
to get the Usage Help:
```bash
Usage: rml_report_generator [OPTIONS] [MAPPING_SUITE_ID]

  Generates RML modules report file for Mapping Suite.

Options:
  -m, --opt-mappings-folder TEXT
  --help                                      Show this message and exit.
```

### API
#### ID Manager API
##### Start local API server
To start the API server:
```bash
api-id_manager-start-server
```
Output:
```bash
uvicorn --host localhost --port 8000 ted_sws.id_manager.entrypoints.api.main:app --reload
###
See http://localhost:8000/api/v1/docs for API usage.
```
Use:
```bash
api-id_manager-start-server --help
```
to get the cli command Usage Help:
```bash
Usage: api-id_manager-start-server [OPTIONS]

Options:
  -h, --host TEXT
  -p, --port INTEGER
  --help                                      Show this message and exit.
```

<hr>

## Contributing

You are more than welcome to help expand and mature this project. 

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we adhere to [Apache code of conduct](https://www.apache.org/foundation/policies/conduct), please follow it in all your interactions with the project.  

## Licence 

The documents, such as reports and specifications are licenced under a [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/deed.en).

The source code and other scripts are licenced under [EUPL v1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12) licence.
