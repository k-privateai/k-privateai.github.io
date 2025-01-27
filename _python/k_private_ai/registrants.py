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
        number_3rd_seminar_participants: int = 0
        number_both_seminar_participants: int = 0
        for registrant in sorted(
            self.email_registrant_map.values(),
            key=lambda k_pai_registrant: k_pai_registrant.name,  # type:ignore
            reverse=False,
        ):
            if registrant.attend_3rd_seminar:
                number_3rd_seminar_participants += 1

            if registrant.attend_2nd_seminar and registrant.attend_3rd_seminar:
                number_both_seminar_participants += 1

            print(registrant)

        print(len(self.email_registrant_map))
        print(number_3rd_seminar_participants)
        print(number_both_seminar_participants)
