from unittest import TestCase, main
from bacon_com_ovos import Bacon


class TestBaconComOvos(TestCase):

    def test_bacon_com_ovos_deve_levantar_assertion_error_se_nao_receber_int(self):
        bacon = Bacon()
        with self.assertRaises(AssertionError):
            bacon.bacon_com_ovos('')


if __name__ == '__main__':
    main()