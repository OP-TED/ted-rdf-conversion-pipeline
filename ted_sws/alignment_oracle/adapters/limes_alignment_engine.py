import pathlib
from jinja2 import Environment, PackageLoader

TEMPLATES = Environment(loader=PackageLoader("ted_sws.alignment_oracle.resources", "templates"))
LIMES_CONFIG_TEMPLATE = "limes_config.jinja2"



def function():
    limes_config_params = LimesConfigParams(source=DataSource(),
                                            target=DataSource(),
                                            acceptance=DataResult(),
                                            review=DataResult()).dict()
    print(TEMPLATES.get_template(LIMES_CONFIG_TEMPLATE).render(limes_config_params))

function()

class LimesAlignmentEngine:

    def __init__(self, limes_executable_path: pathlib.Path):
        ...

    def execute(self, config_builder: LimesAlignmentEngineConfigBuilder):
        ...
