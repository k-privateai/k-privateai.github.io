"""
A class for seminar registrant for the 3rd seminar on 22-Jan-2025
"""

from pandas import Series
from phonenumbers import parse, PhoneNumber, NumberParseException

from k_private_ai.utils import get_data, get_phone_number_str


class KPaiMember02:
    def __init__(self, row: Series) -> None:
        self.organizer: str | None = get_data(row["organizer"])
        self.member_02: bool = row["member by 2nd seminar"] == "o"
        self.attend_2nd_seminar: bool = row["2nd seminar participation"] == "o"
        self.last_name: str | None = get_data(row["last name"])
        self.first_name: str | None = get_data(row["first name"])
        self.english_full_name: str | None = get_data(row["English full name"])
        self.korean_name: str | None = get_data(row["Korean name"])
        self.personal_email: str | None = get_data(row["personal email"])
        self.work_email: str | None = get_data(row["work email"])
        try:
            self.phone_number: PhoneNumber | None = parse(row["phone number"])
        except (NumberParseException, TypeError):
            self.phone_number = None
        self.company: str | None = get_data(row["company/organization"])
        self.job_title: str | None = get_data(row["job title"])
        self.linkedin: str | None = get_data(row["LinkedIn profile url"])
        self.experience: str | None = get_data(row["Years of experience in industry (as of 2024)"])

    def __repr__(self) -> str:
        return (
            f"Member(\n"
            f"  Organizer: {self.organizer},\n"
            f"  Member: {self.member_02},\n"
            f"  Participation: {self.attend_2nd_seminar},\n"
            f"  Last Name: {self.last_name},\n"
            f"  First Name: {self.first_name},\n"
            f"  Full Name: {self.english_full_name},\n"
            f"  Korean Name: {self.korean_name},\n"
            f"  Personal Email: {self.personal_email},\n"
            f"  Work Email: {self.work_email},\n"
            f"  Phone: {get_phone_number_str(self.phone_number)},\n"
            f"  Company: {self.company},\n"
            f"  Job Title: {self.job_title},\n"
            f"  LinkedIn: {self.linkedin},\n"
            f"  Experience: {self.experience} years\n"
            f")"
        )
