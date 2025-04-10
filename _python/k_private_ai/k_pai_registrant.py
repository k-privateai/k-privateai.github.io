"""
K-PAI registrant
"""

from __future__ import annotations

from logging import Logger, getLogger
from urllib.parse import urlparse, urlunparse, ParseResult

from phonenumbers import PhoneNumber

from k_private_ai.member_02 import KPaiMember02
from k_private_ai.registrant_03 import SeminarRegistrant03
from k_private_ai.utils import get_phone_number_str

logger: Logger = getLogger()


class KPaiRegistrant:
    def __init__(self, registrant: KPaiMember02 | SeminarRegistrant03) -> None:
        self.k_pai_member_02: KPaiMember02 | None = None
        self.seminar_registrant_03: SeminarRegistrant03 | None = None

        if isinstance(registrant, KPaiMember02):
            self.k_pai_member_02 = registrant
        if isinstance(registrant, SeminarRegistrant03):
            self.seminar_registrant_03 = registrant

        self._email: str | None = None
        self._work_email: str | None = None
        self._name: str | None = None
        self._english_full_name: str | None = None
        self._phone_number: PhoneNumber | None = None
        self._company: str | None = None
        self._job_title: str | None = None
        self._linkedin_url: str | None = None
        self._share_info: bool | None = None

        self._attend_1st_seminar: bool = False
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
            self._work_email = self.k_pai_member_02.work_email
            self._name = (
                self.k_pai_member_02.korean_name
                if self.k_pai_member_02.korean_name is not None
                else self.k_pai_member_02.english_full_name
            )
            self._attend_2nd_seminar = self.k_pai_member_02.attend_2nd_seminar

        assert self._email is not None

        if self._email == "ywha.p2o.@gmail.com":
            self._email = "ywha.p2o@gmail.com"

    def __repr__(self) -> str:
        assert self.name is not None, self.email
        return (
            f"KPaiRegistrant({self.attend_1st_seminar_ox_str}, {self.attend_2nd_seminar_ox_str}"
            + f", {self.attend_3rd_seminar_ox_str}, {self.share_info}"
            + f", {self.name}, {self.email}, {get_phone_number_str(self.phone_number)}"
            + f", {self.company}, {self.job_title}, {self.linkedin_url})"
        )

    def complete_fields(self) -> None:
        assert not (self.k_pai_member_02 is None and self.seminar_registrant_03 is None)
        self._complete_field("_english_full_name", "english_full_name")
        self._complete_field("_company", "company")
        self._complete_field("_job_title", "job_title")
        self._complete_field("_phone_number", "phone_number")
        self._complete_field("_linkedin_url", "linkedin")
        if self.seminar_registrant_03 is not None:
            self._share_info = (
                self.seminar_registrant_03.share_info is not None
                and self.seminar_registrant_03.share_info.lower().startswith("yes")
            )

        if self._linkedin_url is not None:
            url: ParseResult = urlparse(self._linkedin_url)
            self._linkedin_url = urlunparse(("https", url.netloc, url.path, url.params, "", ""))

    def _complete_field(self, this_field_name: str, field_name: str) -> None:
        if (
            self.k_pai_member_02 is not None
            and self.k_pai_member_02.__dict__[field_name] is not None
        ):
            self.__dict__[this_field_name] = self.k_pai_member_02.__dict__[field_name]

        if (
            self.seminar_registrant_03 is not None
            and self.seminar_registrant_03.__dict__[field_name] is not None
        ):
            self.__dict__[this_field_name] = self.seminar_registrant_03.__dict__[field_name]

        if self.k_pai_member_02 is not None and self.seminar_registrant_03 is not None:
            if not (
                self.k_pai_member_02.__dict__[field_name]
                == self.seminar_registrant_03.__dict__[field_name]
            ):
                logger.warning(
                    f"field value conflict: {field_name}"
                    + " - "
                    + f"{self.k_pai_member_02.__dict__[field_name]}"
                    + " != "
                    + f"{self.seminar_registrant_03.__dict__[field_name]}"
                    + " -> "
                    + f"{self.__dict__[this_field_name]}"
                )

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def email(self) -> str | None:
        return self._email

    @property
    def work_email(self) -> str | None:
        return self._work_email

    @property
    def phone_number(self) -> PhoneNumber | None:
        return self._phone_number

    @property
    def company(self) -> str | None:
        return self._company

    @property
    def job_title(self) -> str | None:
        return self._job_title

    @property
    def linkedin_url(self) -> str | None:
        return self._linkedin_url

    @property
    def share_info(self) -> bool | None:
        return self._share_info

    @property
    def attend_1st_seminar(self) -> bool:
        return self._attend_1st_seminar

    @attend_1st_seminar.setter
    def attend_1st_seminar(self, value: bool) -> None:
        self._attend_1st_seminar = value

    @property
    def attend_2nd_seminar(self) -> bool:
        return self._attend_2nd_seminar

    @property
    def attend_3rd_seminar(self) -> bool:
        return self._attend_3rd_seminar

    @property
    def attend_1st_seminar_ox_str(self) -> str:
        return "O" if self.attend_1st_seminar else "X"

    @property
    def attend_2nd_seminar_ox_str(self) -> str:
        return "O" if self.attend_2nd_seminar else "X"

    @property
    def attend_3rd_seminar_ox_str(self) -> str:
        return "O" if self.attend_3rd_seminar else "X"

    @property
    def emails(self) -> list[str]:
        assert self.email is not None
        return ([self.email] if "@" in self.email else []) + (
            [] if self.work_email is None else [self.work_email]
        )

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

    @staticmethod
    def get_col_names_for_excel_file() -> list[str]:
        return [
            "name",
            "1st seminar",
            "2nd seminar",
            "3rd seminar",
            "share info",
            "company",
            "job title",
            "email",
            "phone number",
            "LinkedIn",
        ]

    @property
    def excel_fields(self) -> list[str | None]:
        return [
            self.name,
            "o" if self.attend_1st_seminar else "",
            "o" if self.attend_2nd_seminar else "",
            "o" if self.attend_3rd_seminar else "",
            self.share_info if self.share_info is None else ("o" if self.share_info else "x"),
            self.company,
            self.job_title,
            self.email,
            get_phone_number_str(self.phone_number),
            self.linkedin_url,
        ]
