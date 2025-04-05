"""
convert Google Sheet downloaded as .tsv file into .csv for Google Contacts App
"""

import os
import re
from typing import Any

import numpy as np
from pandas import read_csv, Series, DataFrame

from freq_used.google.contacts.utils import get_label_str, is_home_email


# def convert_person_info_to_dict(person: dict[str, Any], kisoo: int) -> dict[str, Any]:
def convert_person_info_to_dict(person: Series) -> dict[str, Any]:
    assert isinstance(person["name"], str), person["name"].__class__
    assert isinstance(person["company"], (str, float)), (
        person["company"],
        person["company"].__class__,
    )
    assert isinstance(person["job title"], (str, float)), (
        person["job title"],
        person["job title"].__class__,
    )
    assert isinstance(person["email"], str), person["email"].__class__
    assert isinstance(person["phone number"], (str, float)), (
        person["phone number"],
        person["phone number"].__class__,
    )
    assert isinstance(person["LinkedIn"], (str, float)), (
        person["LinkedIn"],
        person["LinkedIn"].__class__,
    )
    assert isinstance(person["membership"], np.bool), (
        person["name"],
        person["membership"],
        person["membership"].__class__,
    )
    assert isinstance(
        person[
            "Would you like to join the K-PAI forum membership? You're eligible to become a K-PAI forum member if you've attended two or more of our seminars! Learn more: https://k-privateai.github.io/_x"
        ],
        (str, float),
    ), person[
        "Would you like to join the K-PAI forum membership? You're eligible to become a K-PAI forum member if you've attended two or more of our seminars! Learn more: https://k-privateai.github.io/_x"
    ].__class__

    res: dict[str, Any] = dict()

    res["Last Name"], res["First Name"] = parse_name(person["name"])
    if isinstance(person["company"], str):
        res["Organization Name"] = person["company"]

    if isinstance(person["job title"], str):
        res["Organization Title"] = person["job title"]

    res["E-mail 1 - Label"] = "* Home" if is_home_email(person["email"]) else "* Work"
    res["E-mail 1 - Value"] = person["email"]

    if isinstance(person["phone number"], str):
        res["Phone 1 - Label"] = "Mobile"
        res["Phone 1 - Value"] = convert_phone_number(person["phone number"])
        # print(
        #     f'{person["phone number"]:20} -> {res["Phone 1 - Value"]:20}'
        #     + f' - {res["Last Name"]}, {res["First Name"]}'
        # )

    if isinstance(person["LinkedIn"], str):
        res["Website 1 - Label"] = None
        res["Website 1 - Value"] = get_linkedin_url(person["LinkedIn"])
        # print(res["Website 1 - Value"])

    labels: list[str] = ["k-pai-attendee (Shared)"]
    if person["membership"]:
        labels.append("k-pai-member (Shared)")

    res["Labels"] = get_label_str(*labels)

    return res


def parse_name(name: str) -> tuple[str, str]:
    name = name.strip()
    tokens: list[str] = name.split()
    if re.match(r"[a-zA-Z]", name):
        return tokens[-1], " ".join(tokens[:-1])

    if len(tokens) == 1:
        return name[0], name[1:]
    elif len(tokens) == 2:
        return tokens[1], tokens[0]
    else:
        assert False, (tokens, name)


def convert_phone_number(phone: str) -> str:
    if phone == "+826693503630":
        return "+1 " + phone[3:]
    if phone == "+818033155689":
        return "+1 " + phone[3:]
    if phone.startswith("+1") and phone[2] != " ":
        return "+1 " + phone[2:]
    if phone.startswith("+82") and phone[3] != " ":
        return "+82 " + phone[3:]
    return phone


def get_linkedin_url(url: str) -> str:
    return url.split("?")[0]


if __name__ == "__main__":

    directory: str = "/Users/sungheeyun/workspace/k-privateai.github.io/resource/registrants/"
    google_csv_file_path: str = os.path.join(
        os.curdir, "k-pai-registrants-5-in-google-contacts-format.csv"
    )

    google_sheet_tsv_file: str = os.path.join(directory, "2025-03-12 (~5th) - out.tsv")

    df: DataFrame = read_csv(google_sheet_tsv_file, sep="\t")

    google_contact_df: DataFrame = DataFrame(
        [convert_person_info_to_dict(df.iloc[row_idx]) for row_idx in range(df.shape[0])]
    )

    google_contact_df.to_csv(google_csv_file_path)
