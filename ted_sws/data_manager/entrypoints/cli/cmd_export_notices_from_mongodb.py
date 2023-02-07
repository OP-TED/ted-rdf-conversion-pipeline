from typing import List

import click
from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner
from ted_sws.data_manager.services.export_notice_from_mongodb import export_notice_by_id

CMD_NAME = "CMD_EXPORT_NOTICES_FROM_MONGODB"

"""
USAGE:
# component_detector --help
"""


class CmdRunner(BaseCmdRunner):

    def __init__(self, notice_ids: List[str] = None, output_folder: str = None, mongodb_client: MongoClient = None):
        super().__init__(name=CMD_NAME)
        self.notice_ids = self._init_list_input_opts(notice_ids)
        self.output_folder = output_folder
        self.mongodb_client = mongodb_client

    def run_cmd(self):
        if self.notice_ids:
            for notice_id in self.notice_ids:
                is_saved, saved_path = export_notice_by_id(notice_id, self.output_folder,
                                                           mongodb_client=self.mongodb_client)
                if is_saved:
                    self.log(f"Notice {notice_id} saved in {saved_path}.")
                else:
                    self.log(f"Notice {notice_id} is not saved.")
        else:
            self.log("List with notices is empty.")

        return self.run_cmd_result()


def run(notice_id=None,
        output_folder: str = None,
        mongodb_auth_url: str = None,
        mongodb_client: MongoClient = None):
    """
    This is the bridge function from CLI to CmdRunner, where input data is prepared
    :param notice_id:
    :param output_folder:
    :param mongodb_auth_url:
    :param mongodb_client:
    :return:
    """
    if mongodb_auth_url:
        mongodb_client = MongoClient(mongodb_auth_url)
    elif not mongodb_client:
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)

    cmd = CmdRunner(
        notice_ids=list(notice_id or []),
        output_folder=output_folder,
        mongodb_client=mongodb_client
    )
    cmd.run()


@click.command()
@click.option('-n', '--notice-id', required=True, multiple=True)
@click.option('-o', '--output-folder', required=False, default=".")
@click.option('-mau', '--mongodb-auth-url', required=False)
def main(notice_id, output_folder, mongodb_auth_url):
    """
    This CLI tool will export/unpack a Notice from database
    :param notice_id:
    :param output_folder:
    :param mongodb_auth_url:
    :return:
    """
    run(notice_id=notice_id, output_folder=output_folder, mongodb_auth_url=mongodb_auth_url)


if __name__ == '__main__':
    main()
