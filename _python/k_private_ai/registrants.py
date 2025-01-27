"""
Collection of K-PAI registrants
"""

from k_private_ai.registrant import KPaiRegistrant
from k_private_ai.member_02 import KPaiMember02
from k_private_ai.registrant_03 import SeminarRegistrant03


class KPaiRegistrantCollection:
    def __init__(self) -> None:
        self.email_registrant_map: dict[str, KPaiRegistrant] = dict()

    def add_registrant(self, registrant: KPaiMember02 | SeminarRegistrant03) -> None:
        k_pai_registrant: KPaiRegistrant = KPaiRegistrant(registrant)

        email = k_pai_registrant.email
        assert email is not None, k_pai_registrant

        if email in self.email_registrant_map:
            self.email_registrant_map[email].combine(k_pai_registrant)
        else:
            self.email_registrant_map[email] = k_pai_registrant

    def print_registrants(self) -> None:
        tt: int = 0
        for registrant in sorted(
            self.email_registrant_map.values(),
            key=lambda k_pai_registrant: k_pai_registrant.name,  # type:ignore
            reverse=False,
        ):
            print(registrant)
            tt += 1 if registrant.attend_3rd_seminar == "O" else 0

        print(len(self.email_registrant_map))
        print(tt)
