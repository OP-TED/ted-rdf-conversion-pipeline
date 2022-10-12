from ted_sws import config
from ted_sws.alignment_oracle.adapters.limes_alignment_engine import LimesAlignmentEngine
from ted_sws.alignment_oracle.model.limes_config import LimesConfigParams


def generate_alignment_links(limes_config_params: LimesConfigParams):
    limes_alignment_engine = LimesAlignmentEngine(limes_executable_path=config.LIMES_ALIGNMENT_PATH)
    limes_alignment_engine.execute(limes_config_params=limes_config_params)



