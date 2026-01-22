"""
Collection of K-PAI registrants
"""

from logging import getLogger, Logger
from functools import reduce

from pandas import DataFrame, ExcelWriter

from k_private_ai.k_pai_registrant import KPaiRegistrant
from k_private_ai.member_02 import KPaiMember02
from k_private_ai.registrant_03 import SeminarRegistrant03

logger: Logger = getLogger()


class KPaiRegistrantCollection:
    def __init__(self) -> None:
        self._email_registrant_map: dict[str, KPaiRegistrant] = dict()
        self._fields_completed: bool = False

    def add_registrant(self, registrant: KPaiMember02 | SeminarRegistrant03) -> None:
        self._fields_completed = False

        k_pai_registrant: KPaiRegistrant = KPaiRegistrant(registrant)

        email = k_pai_registrant.email
        assert email is not None, k_pai_registrant

        if email in self._email_registrant_map:
            self._email_registrant_map[email].combine(k_pai_registrant)
        else:
            self._email_registrant_map[email] = k_pai_registrant

    def complete_fields(self) -> None:
        if self._fields_completed:
            return

        for registrant in self._email_registrant_map.values():
            registrant.complete_fields()

        self._fields_completed = True

    def analyze(self) -> None:
        self.complete_fields()

        number_3rd_seminar_participants: int = 0
        number_double_seminar_participants: int = 0
        registrants: list[KPaiRegistrant] = sorted(
            self._email_registrant_map.values(),
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

            if (
                registrant.attend_1st_seminar
                + registrant.attend_2nd_seminar
                + registrant.attend_3rd_seminar
                >= 2
            ):
                number_double_seminar_participants += 1
                print(registrant)

        logger.info(f"Total # registrants: {len(self._email_registrant_map)}")
        logger.info(f"# 3rd seminar participants: {number_3rd_seminar_participants}")
        logger.info(
            f"# people who attended both 2nd and 3rd seminar: {number_double_seminar_participants}"
        )

    def to_excel(self, excel_file_path: str, sheet_name: str) -> None:
        self.complete_fields()

        with ExcelWriter(excel_file_path) as writer:
            DataFrame(
                [
                    registrant.excel_fields
                    for registrant in sorted(
                        self._email_registrant_map.values(),
                        key=lambda k_pai_registrant: (
                            k_pai_registrant.name,
                            k_pai_registrant.email,
                        ),
                    )
                ],
                columns=KPaiRegistrant.get_col_names_for_excel_file(),
            ).to_excel(writer, sheet_name=sheet_name, index=False)

    @property
    def all_emails(self) -> list[str]:
        self.complete_fields()
        return reduce(
            list.__add__, [registrant.emails for registrant in self._email_registrant_map.values()]
        )

    def find_by_name(self, name: str) -> list[KPaiRegistrant]:
        return [
            registrant
            for registrant in self._email_registrant_map.values()
            if registrant.name == name
        ]
