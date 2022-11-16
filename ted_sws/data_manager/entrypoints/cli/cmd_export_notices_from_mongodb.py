from typing import List

import click
from pathlib import Path

from pymongo import MongoClient

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner
from ted_sws.data_manager.services.export_notice_from_mongodb import export_notice_by_id

CMD_NAME = "CMD_EXPORT_NOTICES_FROM_MONGODB"

"""
USAGE:
# component_detector --help
"""


class CmdRunner(BaseCmdRunner):

    def __init__(self, notice_ids: List[str] = None, output_folder: str = None):
        super().__init__(name=CMD_NAME)
        self.notice_ids = self._init_list_input_opts(notice_ids)
        self.output_folder = output_folder

    def run_cmd(self):
        error = None
        try:
            if self.notice_ids:
                for notice_id in self.notice_ids:
                    is_saved, saved_path = export_notice_by_id(notice_id, self.output_folder)
                    if is_saved:
                        self.log(f"Notice {notice_id} saved in {saved_path}.")
                    else:
                        self.log(f"Notice {notice_id} is not saved.")
            else:
                self.log("List with notices is empty.")
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


@click.command()
@click.option('-n', '--notice-id', required=True, multiple=True)
@click.option('-o', '--output-folder', required=False, default=".")
def main(notice_id, output_folder):
    """

    """
    cmd = CmdRunner(
        notice_ids=list(notice_id),
        output_folder=output_folder
    )
    cmd.run()


if __name__ == '__main__':
    main()
