"""Pruebas automáticas.  Ejecutar:  python -m unittest -v test_tarea"""
import tempfile
import unittest
from pathlib import Path

from conjuntos import (ErrorEntrada, calcular_conjuntos, gramatica_desde_texto,
                       leer_gramatica)

RAIZ = Path(__file__).resolve().parent
EPS, FIN = "ε", "$"


def C(texto):
    """C("uno dos ε") -> {"uno", "dos", "ε"}"""
    return set(texto.split())


class TestLectura(unittest.TestCase):
    def test_alternativas_y_epsilon(self):
        g = gramatica_desde_texto("A -> a B | eps\nB -> b | ε")
        self.assertEqual(g.producciones, [("A", ["a", "B"]), ("A", []), ("B", ["b"]), ("B", [])])
        self.assertEqual(g.no_terminales, ["A", "B"])
        self.assertEqual(g.terminales, ["a", "b"])
        self.assertEqual(g.inicial, "A")

    def test_flecha_unicode_y_comentarios(self):
        g = gramatica_desde_texto("# comentario\n\nS → a S   # fin de línea\nS -> b")
        self.assertEqual(g.producciones, [("S", ["a", "S"]), ("S", ["b"])])

    def test_rechaza_formato_invalido(self):
        for texto in ["S a b", "A B -> c", "-> a", "S -> a $", "", "# solo comentario"]:
            with self.subTest(texto=texto):
                with self.assertRaises(ErrorEntrada):
                    gramatica_desde_texto(texto)

    def test_archivo_con_bom(self):
        # el Bloc de notas de Windows puede guardar el archivo con BOM
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "g.txt"
            ruta.write_text("S -> a S | ε\n", encoding="utf-8-sig")
            self.assertEqual(leer_gramatica(ruta).inicial, "S")


class TestEjemplosDeClase(unittest.TestCase):
    """Los ejemplos resueltos en las diapositivas de la clase."""

    def test_ejemplo_primeros_siguientes(self):
        g = gramatica_desde_texto("A -> B C | ant A all\nB -> big C | ε\nC -> cat | cow")
        prim, sig, pred = calcular_conjuntos(g)
        self.assertEqual(prim, {"A": C("ant big cat cow"), "B": C("big ε"), "C": C("cat cow")})
        self.assertEqual(sig["A"], C("all $"))
        self.assertEqual(sig["B"], C("cat cow"))
        # C también queda al final de B -> big C, así que recibe SIGUIENTES(B)
        self.assertEqual(sig["C"], C("all $ cat cow"))
        self.assertEqual(pred, [C("big cat cow"), C("ant"), C("big"),
                                C("cat cow"), C("cat"), C("cow")])

    def test_actividad_guiada(self):
        g = gramatica_desde_texto("S -> A B C\nA -> uno | ε\nB -> dos\nC -> tres | ε")
        prim, sig, _ = calcular_conjuntos(g)
        self.assertEqual(prim, {"S": C("uno dos"), "A": C("uno ε"),
                                "B": C("dos"), "C": C("tres ε")})
        self.assertEqual(sig, {"S": C("$"), "A": C("dos"), "B": C("tres $"), "C": C("$")})


class TestEjercicio1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        g = leer_gramatica(RAIZ / "grammars" / "gramatica1.txt")
        cls.prim, cls.sig, cls.pred = calcular_conjuntos(g)

    def test_primeros(self):
        self.assertEqual(self.prim, {
            "S": C("uno tres cuatro cinco seis"),
            "A": C("tres cuatro cinco seis ε"),
            "B": C("cuatro seis ε"),
            "C": C("cinco ε"),
            "D": C("seis ε"),
        })

    def test_siguientes(self):
        self.assertEqual(self.sig, {
            "S": C("dos $"),
            "A": C("uno tres"),
            "B": C("uno dos tres cinco seis $"),
            "C": C("uno dos tres seis $"),
            "D": C("uno dos tres cuatro seis $"),
        })

    def test_prediccion(self):
        self.assertEqual(self.pred, [
            C("uno tres cuatro cinco seis"),    # S -> A uno B C
            C("uno tres cuatro cinco seis"),    # S -> S dos
            C("uno tres cuatro cinco seis"),    # A -> B C D
            C("tres cuatro cinco seis"),        # A -> A tres
            C("uno tres"),                      # A -> ε
            C("cuatro seis"),                   # B -> D cuatro C tres
            C("uno dos tres cinco seis $"),     # B -> ε
            C("cinco"),                         # C -> cinco D B
            C("uno dos tres seis $"),           # C -> ε
            C("seis"),                          # D -> seis
            C("uno dos tres cuatro seis $"),    # D -> ε
        ])


class TestEjercicio2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        g = leer_gramatica(RAIZ / "grammars" / "gramatica2.txt")
        cls.prim, cls.sig, cls.pred = calcular_conjuntos(g)

    def test_primeros(self):
        self.assertEqual(self.prim, {
            "S": C("uno dos tres cuatro cinco"),
            "A": C("dos ε"),
            "B": C("tres cuatro cinco ε"),
            "C": C("cuatro cinco"),
            "D": C("seis ε"),
        })

    def test_siguientes(self):
        resto = C("uno tres cuatro cinco seis")
        self.assertEqual(self.sig, {"S": C("$"), "A": resto, "B": resto, "C": resto, "D": resto})

    def test_prediccion(self):
        self.assertEqual(self.pred, [
            C("uno dos tres cuatro cinco"),     # S -> A B uno
            C("dos"),                           # A -> dos B
            C("uno tres cuatro cinco seis"),    # A -> ε
            C("cuatro cinco"),                  # B -> C D
            C("tres"),                          # B -> tres
            C("uno tres cuatro cinco seis"),    # B -> ε
            C("cuatro"),                        # C -> cuatro A B
            C("cinco"),                         # C -> cinco
            C("seis"),                          # D -> seis
            C("uno tres cuatro cinco seis"),    # D -> ε
        ])


class TestPropiedades(unittest.TestCase):
    def test_epsilon_nunca_en_siguientes_y_fin_en_inicial(self):
        for nombre in ["gramatica1.txt", "gramatica2.txt"]:
            g = leer_gramatica(RAIZ / "grammars" / nombre)
            _, sig, pred = calcular_conjuntos(g)
            with self.subTest(gramatica=nombre):
                self.assertIn(FIN, sig[g.inicial])
                for a in g.no_terminales:
                    self.assertNotIn(EPS, sig[a])
                for conjunto in pred:
                    self.assertNotIn(EPS, conjunto)


if __name__ == "__main__":
    unittest.main(verbosity=2)
