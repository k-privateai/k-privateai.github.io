"""
parse .tsv file for the Google form summary for the K-PAI 3rd seminar
"""

import os
from pathlib import Path

from pandas import read_csv, DataFrame
from freq_used.logging_utils import set_logging_basic_config

from k_private_ai.registrant_03 import SeminarRegistrant03
from k_private_ai.member_02 import KPaiMember02
from k_private_ai.registrants import KPaiRegistrantCollection

project_root: Path = Path(__file__).parent.parent.parent

if __name__ == "__main__":
    set_logging_basic_config(__file__)

    data_1: DataFrame = read_csv(
        os.path.join(project_root, "resource/registrants", "K-PAI Members - participants.tsv"),
        sep="\t",
    )

    data_2: DataFrame = read_csv(
        os.path.join(
            project_root,
            "resource/registrants",
            "Freezed The 3rd K-PAI Seminar Application (Responses) - Form Responses 1.tsv",
        ),
        sep="\t",
    )

    registrants: KPaiRegistrantCollection = KPaiRegistrantCollection()

    for idx, row in data_1.iterrows():
        registrants.add_registrant(KPaiMember02(row))
        # if idx == 1:
        #     print(KPaiMember02(row))

    for idx, row in data_2.iterrows():
        registrants.add_registrant(SeminarRegistrant03(row))
        # if idx == 20:
        #     print(SeminarRegistrant03(row))

    registrants.print_registrants()
