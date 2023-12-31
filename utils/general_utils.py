def get_table_name_from_email(email: str) -> str:
    parsed_mail = email.split("@")
    return parsed_mail[0] + "_" + parsed_mail[1].split(".")[0]