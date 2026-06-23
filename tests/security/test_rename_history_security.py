from tests.fixtures.rename_inventory import INTENTIONAL_OLD_NAME_REFERENCES


def test_old_name_classifications_do_not_include_secret_values():
    serialized = " ".join(INTENTIONAL_OLD_NAME_REFERENCES.values()).casefold()
    for forbidden in ("password", "secret", "token", "session"):
        assert forbidden not in serialized
