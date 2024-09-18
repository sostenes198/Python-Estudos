from unittest import TestCase, main
from calculadora import soma


class TestCalculadora(TestCase):

    def test_soma_5_e_5_deve_retornar_10(self):
        self.assertEqual(soma(5, 5), 10)

    def test_soma_varias_entradas(self):
        x_y_saidas = (
            (10, 10, 20),
            (-10, 10, 0),
            (-20, 10, -10),
            (20, -10, 10),
            (20, -22, -2),
            (0, 0, 0),
            (-1, -2, -3)
        )

        for x_y_saida in x_y_saidas:
            with self.subTest(x_y_saida=x_y_saida):
                x, y, saida = x_y_saida
                self.assertEqual(soma(x, y), saida)


if __name__ == '__main__':
    main()
