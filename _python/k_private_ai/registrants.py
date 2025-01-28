"""
Collection of K-PAI registrants
"""

from logging import getLogger, Logger

from pandas import DataFrame, ExcelWriter

from k_private_ai.registrant import KPaiRegistrant
from k_private_ai.member_02 import KPaiMember02
from k_private_ai.registrant_03 import SeminarRegistrant03

logger: Logger = getLogger()


class KPaiRegistrantCollection:
    def __init__(self) -> None:
        self.email_registrant_map: dict[str, KPaiRegistrant] = dict()
        self._fields_completed: bool = False

    def add_registrant(self, registrant: KPaiMember02 | SeminarRegistrant03) -> None:
        self._fields_completed = False

        k_pai_registrant: KPaiRegistrant = KPaiRegistrant(registrant)

        email = k_pai_registrant.email
        assert email is not None, k_pai_registrant

        if email in self.email_registrant_map:
            self.email_registrant_map[email].combine(k_pai_registrant)
        else:
            self.email_registrant_map[email] = k_pai_registrant

    def complete_fields(self) -> None:
        if self._fields_completed:
            return

        for registrant in self.email_registrant_map.values():
            registrant.complete_fields()

        self._fields_completed = True

    def analyze(self) -> None:
        self.complete_fields()

        number_3rd_seminar_participants: int = 0
        number_both_seminar_participants: int = 0
        registrants: list[KPaiRegistrant] = sorted(
            self.email_registrant_map.values(),
            key=lambda k_pai_registrant: (
                k_pai_registrant.name,
                k_pai_registrant.email,
            ),  # type:ignore
            reverse=False,
        )
        for idx, registrant in enumerate(registrants):
            if idx < len(registrants) - 1 and registrant.name == registrants[idx + 1].name:
                logger.warning(f"redundant name: {registrant.name}")

            if registrant.attend_3rd_seminar:
                number_3rd_seminar_participants += 1

            if registrant.attend_2nd_seminar and registrant.attend_3rd_seminar:
                number_both_seminar_participants += 1
                print(registrant)

        logger.info(f"Total # registrants: {len(self.email_registrant_map)}")
        logger.info(f"# 3rd seminar participants: {number_3rd_seminar_participants}")
        logger.info(
            f"# people who attended both 2nd and 3rd seminar: {number_both_seminar_participants}"
        )

    def to_excel(self, excel_file_path: str, sheet_name: str) -> None:
        self.complete_fields()

        with ExcelWriter(excel_file_path) as writer:
            DataFrame(
                [
                    registrant.excel_fields
                    for registrant in sorted(
                        self.email_registrant_map.values(),
                        key=lambda k_pai_registrant: (
                            k_pai_registrant.name,
                            k_pai_registrant.email,
                        ),
                    )
                ],
                columns=KPaiRegistrant.get_col_names_for_excel_file(),
            ).to_excel(writer, sheet_name=sheet_name, index=False)
