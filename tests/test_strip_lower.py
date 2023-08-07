from wordleapi.utils import strip_lower


def test_strip_lower():
    assert strip_lower(None) is None, "None returns None"
    assert strip_lower("") == "", '"" returns ""'
    assert strip_lower("   ") == "", '"   " returns ""'
    assert strip_lower("azerty") == "azerty", '"azerty" returns "azerty"'
    assert strip_lower("   AzErTy    ") == "azerty", '"   AzErTy    " returns "azerty"'
