from normalize import is_permanently_closed, normalize_phone, parse_input_id


def test_normalize_plus62():
    # Arrange
    raw = "+62 812-3456-7890"
    # Act
    result = normalize_phone(raw)
    # Assert
    assert result == "081234567890"


def test_normalize_area_code_without_zero():
    assert normalize_phone("62217654321") == "0217654321"


def test_normalize_keeps_leading_zero():
    assert normalize_phone("(021) 765-4321") == "0217654321"


def test_normalize_mobile_without_zero():
    assert normalize_phone("81298765432") == "081298765432"


def test_normalize_takes_first_of_many():
    assert normalize_phone("0811111111 / 0822222222") == "0811111111"


def test_normalize_rejects_junk():
    assert normalize_phone("-") is None
    assert normalize_phone("") is None
    assert normalize_phone(None) is None
    assert normalize_phone("123") is None  # terlalu pendek


def test_permanently_closed():
    assert is_permanently_closed("CLOSED_PERMANENTLY")
    assert is_permanently_closed("permanently closed")
    assert not is_permanently_closed("open")
    assert not is_permanently_closed(None)


def test_parse_input_id():
    assert parse_input_id("31.71.01|mobil") == ("31.71.01", "mobil")
    assert parse_input_id("31.71.01|motor") == ("31.71.01", "motor")
    assert parse_input_id("31.71.01|aneh") == ("31.71.01", None)
    assert parse_input_id("31.71.01") == ("31.71.01", None)
    assert parse_input_id(None) == (None, None)
