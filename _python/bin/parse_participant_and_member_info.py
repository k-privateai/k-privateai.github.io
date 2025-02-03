"""
parse .tsv file for the Google form summary for the K-PAI 3rd seminar
"""

import os
from pathlib import Path
from logging import Logger, getLogger

from pandas import read_csv, DataFrame
from freq_used.logging_utils import set_logging_basic_config

from k_private_ai.registrant_03 import SeminarRegistrant03
from k_private_ai.member_02 import KPaiMember02
from k_private_ai.registrants import KPaiRegistrantCollection
from k_private_ai.k_pai_registrant import KPaiRegistrant

logger: Logger = getLogger()

project_root: Path = Path(__file__).parent.parent.parent

if __name__ == "__main__":
    set_logging_basic_config(__file__)

    registrants_dir: str = os.path.join(project_root, "resource/registrants")

    data_12: DataFrame = read_csv(
        os.path.join(registrants_dir, "K-PAI Members - participants.tsv"),
        sep="\t",
    )

    data_3: DataFrame = read_csv(
        os.path.join(
            registrants_dir,
            "Frozen The 3rd K-PAI Seminar Application (Responses) - Form Responses 1.tsv",
        ),
        sep="\t",
    )

    registrants: KPaiRegistrantCollection = KPaiRegistrantCollection()

    for idx, row in data_12.iterrows():
        registrants.add_registrant(KPaiMember02(row))
        # if idx == 1:
        #     print(KPaiMember02(row))

    for idx, row in data_3.iterrows():
        registrants.add_registrant(SeminarRegistrant03(row))
        # if idx == 20:
        #     print(SeminarRegistrant03(row))

    with open(os.path.join(registrants_dir, "participants-01.txt")) as fid:
        for name in fid:
            name = name.strip()
            registrant_list: list[KPaiRegistrant] = registrants.find_by_name(name)
            assert len(registrant_list) == 1, (registrant_list, len(registrant_list))
            registrant_list[0].attend_1st_seminar = True

    registrants.analyze()
    registrants.to_excel("registrants.xlsx", "up to 3rd seminar")
    logger.info(", ".join(registrants.all_emails))
