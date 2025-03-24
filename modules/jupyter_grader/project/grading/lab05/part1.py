from typing import Any, Callable
from ..types import Checker
from abc import ABC, abstractmethod
import inspect
from ..utils import banner
from colorama import Fore
import unittest
import types


class Tester(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check(self, obj: Any):
        pass


def check_methods(obj: Any, methods: dict[str, tuple[int, int]]) -> bool:
    for name, inout in methods.items():
        inputs: int = inout[0]
        if not hasattr(obj, name):
            banner(
                Fore.RED
                + f"ERROR: la clase no contiene el metodo '{name}' :face_with_spiral_eyes:"
            )
            return False

        method = getattr(obj, name)
        if type(method) != types.FunctionType:
            banner(Fore.RED + f"ERROR: '{name}' no es un metodo :melting_face:")
            return False

        arguments: int = (
            len(inspect.getfullargspec(method).args) - 1
        )  # sin incluir self
        if arguments != inputs:
            banner(
                Fore.RED
                + f"ERROR: el metodo {name} no contiene la cantidad "
                + f"de entradas esperadas, tiene {arguments}, se esperaban {inputs} :woozy_face:"
            )
            return False

    return True


class BSTTester(Tester):
    class TestBSTreeContainer(unittest.TestCase):
        longMessage = True

    def __init__(self) -> None:
        super().__init__()
        self.methods: dict[str, tuple[int, int]] = {
            "__init__": (0, 0),
            "get_root": (0, 1),
            "insert": (1, 0),
            "preorder_tree_walk": (1, 1),
            "postorder_tree_walk": (1, 1),
            "search": (2, 1),
            "minimum": (1, 1),
            "maximum": (1, 1),
            "successor": (1, 1),
            "predecessor": (1, 1),
        }

    def create_tests(self, bstClass: Any) -> list[Callable]:
        def test_preorder_tree_walk(self: unittest.TestCase):
            t = bstClass()
            t.insert(6)
            t.insert(5)
            t.insert(7)
            t.insert(2)
            t.insert(5)
            t.insert(8)

            expected = [6, 5, 2, 5, 7, 8]
            got = t.preorder_tree_walk(t.get_root())
            self.assertEqual(expected, got, "el preorden no da el resultado esperado")

        def test_postorder_tree_walk(self: unittest.TestCase):
            t = bstClass()
            t.insert(6)
            t.insert(5)
            t.insert(7)
            t.insert(2)
            t.insert(5)
            t.insert(8)

            expected = [2, 5, 5, 8, 7, 6]
            got = t.postorder_tree_walk(t.get_root())
            self.assertEqual(expected, got, "el postorden no da el resultado esperado")

        def test_search(self: unittest.TestCase):
            t = bstClass()
            t.insert(6)
            t.insert(5)
            t.insert(7)
            t.insert(2)
            t.insert(5)
            t.insert(8)

            s = t.search(t.get_root(), 8)
            self.assertIsNotNone(
                s,
                "la busqueda en el arbol debe responder con un nodo si este existe en el arbol",
            )

            s = t.search(t.get_root(), 10)
            self.assertIsNone(
                s,
                "la busqueda en el arbol debe responder con None si el elemento buscado no existe",
            )

        def test_minimum(self: unittest.TestCase):
            t = bstClass()
            m = t.minimum(t.get_root())
            self.assertIsNone(
                m, "no debe haber minimo si no existe ningun elemento en el arbol"
            )

            t.insert(6)
            t.insert(5)
            t.insert(7)
            t.insert(2)
            t.insert(5)
            t.insert(8)

            m = t.minimum(t.get_root())
            self.assertIsNotNone(
                m, "debe existir un minimo si hay elementos en el arbol"
            )
            self.assertEqual(
                2, m.key, "el elemento minimo no corresponde con el esperado"
            )

        def test_maximum(self: unittest.TestCase):
            t = bstClass()
            m = t.maximum(t.get_root())
            self.assertIsNone(
                m, "no debe haber maximo si no existe ningun elemento en el arbol"
            )

            t.insert(6)
            t.insert(5)
            t.insert(7)
            t.insert(2)
            t.insert(5)
            t.insert(8)

            m = t.maximum(t.get_root())
            self.assertIsNotNone(
                m, "debe existir un maximo si hay elementos en el arbol"
            )
            self.assertEqual(
                8, m.key, "el elemento maximo no corresponde con el esperado"
            )

        def test_successor(self: unittest.TestCase):
            t = bstClass()

            nums: list = [ 15, 6, 18, 3, 7, 17, 20, 2, 4, 13, 9, ]
            for n in nums:
                t.insert(n)

            nums.sort()
            nums.append(None)

            for i in range(len(nums) - 1):
                a, succ = nums[i], nums[i + 1]
                m = t.search(t.get_root(), a)
                self.assertIsNotNone(m, "el elemento buscado debe existir en el arbol")
                s = t.successor(m)
                self.assertEqual(
                    succ, s.key if s is not None else None,
                    "el sucesor del elemento seleccionado no coincide con el esperado",
                )

        def test_predecessor(self: unittest.TestCase):
            t = bstClass()

            nums: list = [ 15, 6, 18, 3, 7, 17, 20, 2, 4, 13, 9, ]
            for n in nums:
                t.insert(n)

            nums.sort()
            nums.insert(0, None)

            for i in range(len(nums)-1):
                pred, a = nums[i], nums[i + 1]
                m = t.search(t.get_root(), a)
                self.assertIsNotNone(m, "el elemento buscado debe existir en el arbol")
                s = t.predecessor(m)
                self.assertEqual(
                    pred, s.key if s is not None else None,
                    "el predecesor del elemento seleccionado no coincide con el esperado",
                )

        return [
            test_preorder_tree_walk,
            test_postorder_tree_walk,
            test_search,
            test_minimum,
            test_maximum,
            test_successor,
            test_predecessor,
        ]

    def setup_tests(self, obj: Any):
        tests = self.create_tests(obj)
        for test in tests:
            name = test.__name__
            setattr(BSTTester.TestBSTreeContainer, name, test)

    def execute_test(self):
        unittest.main(
            module=__name__,
            argv=[""],
            defaultTest=f"{BSTTester.__name__}.{BSTTester.TestBSTreeContainer.__name__}",
            verbosity=2,
            exit=False,
        )

    def check(self, obj: Any):
        if not check_methods(obj, self.methods):
            banner(
                Fore.RED
                + f"Verifique que su entrada cumpla las especificaciones del problema"
            )
            return

        self.setup_tests(obj)
        self.execute_test()


class Grader(Checker):
    def __init__(self, name: str, code: int) -> None:
        super().__init__(name, code)
        self.testers: dict[str, Tester] = self.get_testers()

    def get_testers(self) -> dict[str, Tester]:
        return {
            "bst": BSTTester(),
        }

    def grade(self, part: str, answer: Any):
        if part not in self.testers:
            banner(Fore.RED + "ERROR: codigo de ejercicio es invalido :clown_face:")
            return

        tester = self.testers[part]
        tester.check(answer)
