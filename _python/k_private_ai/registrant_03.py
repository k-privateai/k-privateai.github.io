"""
A class for seminar registrant for the 3rd seminar on 22-Jan-2025
"""

from phonenumbers import parse, PhoneNumber, format_number, PhoneNumberFormat

from k_private_ai.utils import get_data


class SeminarRegistrant03:
    def __init__(self, row):
        self.timestamp: str | None = get_data(row["Timestamp"])
        self.email: str | None = get_data(row["Email Address"])
        self.attend_3rd_seminar: bool = get_data(row["attend"]) == "o"
        self.korean_name: str | None = get_data(row["Korean name"])
        self.english_name: str | None = get_data(row["English full name"])
        try:
            self.phone_number: PhoneNumber | None = parse(row["Phone number"], "US")
        except TypeError:
            self.phone_number = None
        self.company: str | None = get_data(row["Current company or organization"])
        self.job_title: str | None = get_data(row["Job title"])
        self.linkedin: str | None = get_data(row["LinkedIn profile URL"])
        self.share_info: str | None = get_data(
            row["Do you want us to share your information with others in our network?"]
        )
        self.expertise: str | None = get_data(
            row["What is your area of expertise within the tech industry?"]
        )
        self.how_heard: str | None = get_data(row["How did you hear about us?"])
        self.will_attend: str | None = get_data(
            row[
                "Will you come to the 3rd K-PAI seminar @ 6pm on 22-Jan-2024?"
                " - The AI Knight Rises: Deep Learning to Flourishing Societies"
            ]
        )
        self.topics: str | None = get_data(
            row[
                "Are there specific topics you want the seminar to cover or discuss?"
                " If so, what are those?"
            ]
        )
        self.goals: str | None = get_data(row["What do you hope to gain from this experience?"])
        self.accommodations: str | None = get_data(
            row[
                "Do you require any special accommodations?"
                " If so, what type of accommodation would you need?"
            ]
        )

    def __repr__(self):
        phone_str: str | None = (
            self.phone_number
            if self.phone_number is None
            else format_number(self.phone_number, PhoneNumberFormat.INTERNATIONAL)
        )
        return (
            f"SeminarRegistrant(\n"
            f"  Timestamp: {self.timestamp},\n"
            f"  Email: {self.email},\n"
            f"  Korean Name: {self.korean_name},\n"
            f"  English Name: {self.english_name},\n"
            f"  Phone: {phone_str},\n"
            f"  Company: {self.company},\n"
            f"  Job Title: {self.job_title},\n"
            f"  LinkedIn: {self.linkedin},\n"
            f"  Share Info: {self.share_info},\n"
            f"  Expertise: {self.expertise},\n"
            f"  How Heard: {self.how_heard},\n"
            f"  Will Attend: {self.will_attend},\n"
            f"  Topics: {self.topics},\n"
            f"  Goals: {self.goals},\n"
            f"  Accommodations: {self.accommodations}\n"
            f")"
        )
