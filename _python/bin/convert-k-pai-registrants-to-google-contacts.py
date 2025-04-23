"""
convert Google Sheet downloaded as .tsv file into .csv for Google Contacts App
"""

import os
import re
from typing import Any
from logging import Logger, getLogger

import numpy as np
from pandas import read_csv, Series, DataFrame

from freq_used.logging_utils import set_logging_basic_config
from freq_used.google.contacts.utils import get_label_str, is_home_email

logger: Logger = getLogger()


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
    assert isinstance(person["membership"], (np.bool, str, float)), (
        person["name"],
        person["membership"],
        person["membership"].__class__,
    )

    long_join_col_name: str = (
        "Would you like to join the K-PAI forum membership? You're eligible to become a K-PAI forum"
        " member if you've attended two or more of our seminars!"
        " Learn more: https://k-privateai.github.io/_x"
    )

    assert long_join_col_name in person or "join" in person, list(person.keys())

    join: str | float = person["join"] if "join" in person else person[long_join_col_name]
    assert isinstance(join, (str, float)), join.__class__

    membership: bool = (
        isinstance(person["membership"], np.bool)
        and person["membership"]
        or isinstance(person["membership"], str)
        and person["membership"] == "o"
    ) and (isinstance(join, str) and join == "o")

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
    if membership:
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


def convert_and_save_to_google_contacts_csv(
    google_sheet_tsv_file: str, google_csv_file_path: str
) -> DataFrame:
    df: DataFrame = read_csv(google_sheet_tsv_file, sep="\t")

    google_contact_df: DataFrame = DataFrame(
        [convert_person_info_to_dict(df.iloc[row_idx]) for row_idx in range(df.shape[0])]
    )

    google_contact_df.to_csv(google_csv_file_path)

    return google_contact_df


def dataframe_set_difference(df1: DataFrame, df2: DataFrame, column_name: str) -> DataFrame:
    """
    Calculates the set difference between two pandas DataFrames based on the values
    in a specified column.

    This function returns a new DataFrame containing the rows from df2 where the value
    in the specified column is NOT present in the corresponding column of df1.  It
    preserves all columns from df2.

    Args:
        df1: The first pandas DataFrame.
        df2: The second pandas DataFrame.
        column_name: The name of the column to use for the set difference.  This
                     column must exist in both DataFrames.

    Returns:
        A new pandas DataFrame containing the rows from df2 that are not in df1
        based on the specified column.  Returns an empty DataFrame if there are no
        differences.  Returns None if the column_name is not found in either
        DataFrame.
    """
    # Check if the column exists in both DataFrames
    if column_name not in df1.columns:
        raise Exception(f"Error: Column '{column_name}' not found in the first DataFrame.")

    if column_name not in df2.columns:
        raise Exception(f"Error: Column '{column_name}' not found in the second DataFrame.")

    # Get the values from the specified column in df1 as a set for faster lookup
    df1_values = set(df1[column_name])

    # Filter df2 to keep only the rows where the specified column's value is not in df1_values
    df_diff = df2[
        ~df2[column_name].isin(df1_values)
    ].copy()  # .copy() to avoid SettingWithCopyWarning

    return df_diff


if __name__ == "__main__":
    set_logging_basic_config(__file__)

    directory: str = "/Users/sungheeyun/workspace/k-privateai.github.io/resource/registrants/"
    k_pai_5_google_csv_file_path: str = os.path.join(
        os.curdir, "k-pai-registrants-5-in-google-contacts-format.csv"
    )
    k_pai_6_google_csv_file_path: str = os.path.join(
        os.curdir, "k-pai-registrants-6-in-google-contacts-format.csv"
    )

    new_k_pai_6_google_csv_file_path: str = os.path.join(
        os.curdir, "new-k-pai-registrants-6-in-google-contacts-format.csv"
    )

    k_pai_5_google_sheet_tsv_file: str = os.path.join(directory, "2025-03-12 (~5th) - out.tsv")
    k_pai_6_google_sheet_tsv_file: str = os.path.join(directory, "2025-04-22 (~6th) - out.tsv")

    google_contact_df_05: DataFrame = convert_and_save_to_google_contacts_csv(
        k_pai_5_google_sheet_tsv_file, k_pai_5_google_csv_file_path
    )

    google_contact_df_06: DataFrame = convert_and_save_to_google_contacts_csv(
        k_pai_6_google_sheet_tsv_file, k_pai_6_google_csv_file_path
    )

    new_google_contact_df_06: DataFrame = dataframe_set_difference(
        google_contact_df_05, google_contact_df_06, "E-mail 1 - Value"
    )

    new_google_contact_df_06.to_csv(new_k_pai_6_google_csv_file_path)
