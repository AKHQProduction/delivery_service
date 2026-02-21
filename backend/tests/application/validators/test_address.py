import pytest

from backend.application.validators.address import (
    normalize_house,
    normalize_street,
)


class TestNormalizeStreet:
    def test_no_prefix(self):
        assert normalize_street("Василя Сліпака") == "василя сліпака"

    def test_strips_whitespace(self):
        assert normalize_street("  Хрещатик  ") == "хрещатик"

    def test_full_ukrainian_vulytsia(self):
        assert normalize_street("вулиця Василя Сліпака") == "василя сліпака"

    def test_abbrev_vul_dot(self):
        assert normalize_street("вул. Василя Сліпака") == "василя сліпака"

    def test_abbrev_vul_no_dot(self):
        assert normalize_street("вул Василя Сліпака") == "василя сліпака"

    def test_full_russian_ulitsa(self):
        assert normalize_street("улица Шевченко") == "шевченко"

    def test_abbrev_ul_dot(self):
        assert normalize_street("ул. Шевченко") == "шевченко"

    def test_prospekt_full(self):
        assert normalize_street("проспект Шевченка") == "шевченка"

    def test_prospekt_abbrev(self):
        assert normalize_street("пр. Шевченка") == "шевченка"

    def test_bulvar(self):
        assert normalize_street("бульвар Лесі Українки") == "лесі українки"

    def test_bulvar_abbrev(self):
        assert normalize_street("б-р Лесі Українки") == "лесі українки"

    def test_provulok(self):
        assert normalize_street("провулок Тихий") == "тихий"

    def test_pereulok(self):
        assert normalize_street("переулок Тихий") == "тихий"

    def test_mikrorayon(self):
        assert normalize_street("мікрорайон Сонячний") == "сонячний"

    def test_mkr_abbrev(self):
        assert normalize_street("мкр. Сонячний") == "сонячний"

    def test_shose(self):
        assert normalize_street("шосе Харківське") == "харківське"

    def test_prefix_not_stripped_if_part_of_word(self):
        assert normalize_street("вулична") == "вулична"

    def test_equivalent_forms(self):
        assert normalize_street("вул. X") == normalize_street("вулиця X")

    @pytest.mark.parametrize(
        ("abbrev", "full", "name"),
        (
            ("вул.", "вулиця", "Шевченка"),
            ("ул.", "улица", "Шевченка"),
            ("пр.", "проспект", "Перемоги"),
            ("б-р", "бульвар", "Лесі Українки"),
            ("мкр.", "мікрорайон", "Сонячний"),
            ("ш.", "шосе", "Харківське"),
        ),
    )
    def test_various_equivalences(self, abbrev: str, full: str, name: str):
        assert normalize_street(f"{abbrev} {name}") == normalize_street(
            f"{full} {name}"
        )


class TestNormalizeHouse:
    def test_plain_number(self):
        assert normalize_house("15") == "15"

    def test_letter_with_space(self):
        assert normalize_house("15 а") == "15а"

    def test_letter_with_dash(self):
        assert normalize_house("15-а") == "15а"

    def test_letter_uppercase(self):
        assert normalize_house("15А") == "15а"

    def test_letter_with_en_dash(self):
        assert normalize_house("15–б") == "15б"

    def test_letter_with_em_dash(self):
        assert normalize_house("15—б") == "15б"

    def test_latin_letter(self):
        assert normalize_house("15a") == "15a"

    def test_strips_whitespace(self):
        assert normalize_house("  15  ") == "15"

    def test_complex_number(self):
        assert normalize_house("15/2") == "15/2"
