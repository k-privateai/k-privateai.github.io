"""
K-PAI registrant
"""

from __future__ import annotations

from logging import Logger, getLogger

from k_private_ai.member_02 import KPaiMember02
from k_private_ai.registrant_03 import SeminarRegistrant03

logger: Logger = getLogger()


class KPaiRegistrant:
    def __init__(self, registrant: KPaiMember02 | SeminarRegistrant03) -> None:
        self.k_pai_member_02: KPaiMember02 | None = None
        self.seminar_registrant_03: SeminarRegistrant03 | None = None

        if isinstance(registrant, KPaiMember02):
            self.k_pai_member_02 = registrant
        if isinstance(registrant, SeminarRegistrant03):
            self.seminar_registrant_03 = registrant

        self._email: str | None = ""
        self._name: str | None = ""
        self._attend_2nd_seminar: bool = False
        self._attend_3rd_seminar: bool = False

        if self.k_pai_member_02 is None:
            assert self.seminar_registrant_03 is not None
            self._email = self.seminar_registrant_03.email
            self._name = self.seminar_registrant_03.korean_name
            self._attend_3rd_seminar = self.seminar_registrant_03.attend_3rd_seminar
        else:
            assert self.seminar_registrant_03 is None
            self._email = (
                self.k_pai_member_02.personal_email
                if self.k_pai_member_02.personal_email is not None
                else self.k_pai_member_02.work_email
            )
            self._name = (
                self.k_pai_member_02.korean_name
                if self.k_pai_member_02.korean_name is not None
                else self.k_pai_member_02.english_full_name
            )
            self._attend_2nd_seminar = self.k_pai_member_02.attend_2nd_seminar

        assert self._email is not None

    def __repr__(self) -> str:
        assert self.name is not None, self.email
        return (
            f"KPaiRegistrant({self.attend_2nd_seminar_str}, {self.attend_3rd_seminar_str}"
            f", {self.name}, {self.email})"
        )

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def email(self) -> str | None:
        return self._email

    @property
    def attend_2nd_seminar(self) -> bool:
        return self._attend_2nd_seminar

    @property
    def attend_3rd_seminar(self) -> bool:
        return self._attend_3rd_seminar

    @property
    def attend_2nd_seminar_str(self) -> str:
        return "O" if self.attend_2nd_seminar else "X"

    @property
    def attend_3rd_seminar_str(self) -> str:
        return "O" if self.attend_3rd_seminar else "X"

    def combine(self, k_pai_registrant: KPaiRegistrant) -> None:
        if self.k_pai_member_02 is None:
            assert k_pai_registrant.k_pai_member_02 is not None, (self.name, self.email)
            assert k_pai_registrant.seminar_registrant_03 is None, (self.name, self.email)
            assert self.name == k_pai_registrant.k_pai_member_02.korean_name, (
                self.name,
                self.email,
            )
            self.k_pai_member_02 = k_pai_registrant.k_pai_member_02
        else:
            assert k_pai_registrant.k_pai_member_02 is None, (self.name, self.email)
            assert k_pai_registrant.seminar_registrant_03 is not None, (self.name, self.email)
            if self.name != k_pai_registrant.seminar_registrant_03.korean_name:
                logger.warning(
                    f"Different names (|{self.name}|"
                    f" & |{k_pai_registrant.seminar_registrant_03.korean_name}|)"
                    f" linked to the same email (={self.email})"
                    f" -> {self.name} is picked!"
                )
            self.seminar_registrant_03 = k_pai_registrant.seminar_registrant_03

        self._attend_2nd_seminar = self._attend_2nd_seminar or k_pai_registrant._attend_2nd_seminar
        self._attend_3rd_seminar = self._attend_3rd_seminar or k_pai_registrant._attend_3rd_seminar
