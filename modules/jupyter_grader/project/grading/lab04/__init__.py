from typing import Any, Callable
from ..types import Checker
from abc import ABC, abstractmethod
import inspect
from ..utils import banner
from colorama import Fore
import unittest
import types


class TestResponse:
    def __init__(self) -> None:
        pass


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


class StackTester(Tester):
    class TestStackContainer(unittest.TestCase):
        longMessage = True

    def __init__(self) -> None:
        super().__init__()
        self.methods: dict[str, tuple[int, int]] = {
            "__init__": (1, 0),
            "push": (1, 0),
            "pop": (0, 1),
            "is_empty": (0, 1),
            "is_full": (0, 1),
        }

    def create_tests(self, stackClass: Any) -> list[Callable]:
        def test_is_empty(self: unittest.TestCase):
            stack = stackClass(10)
            self.assertTrue(
                stack.is_empty(), "la pila debe estar vacia si no tiene nada agregado"
            )

        def test_is_full(self: unittest.TestCase):
            stack = stackClass(10)
            for i in range(10):
                stack.push(i)

            self.assertTrue(
                stack.is_full(),
                "la pila debe esta llena luego de agregarle elementos a maxima capacidad",
            )

        def test_push_pop(self: unittest.TestCase):
            from random import randint

            n = randint(300, 1000)
            stack = stackClass(n)

            for i in range(n):
                stack.push(i)
                self.assertFalse(
                    stack.is_empty(),
                    "la pila no puede estar vacia si se agrego al menos un elemento",
                )

            self.assertTrue(
                stack.is_full(),
                "la pila debe estar llena una vez se llena a maxima capacidad",
            )

            count = 0
            expectedValue = n - 1
            while not stack.is_empty():
                gotValue = stack.pop()
                self.assertEqual(
                    expectedValue,
                    gotValue,
                    "el valor dado de la pila no es el esperado al extraer",
                )
                expectedValue -= 1
                count += 1

            self.assertEqual(
                count,
                n,
                "la cantidad de elementos que se extraen debe ser igual a la cantidad que entro",
            )

        return [
            test_is_empty,
            test_is_full,
            test_push_pop,
        ]

    def setup_tests(self, obj: Any):
        tests = self.create_tests(obj)
        for test in tests:
            name = test.__name__
            setattr(StackTester.TestStackContainer, name, test)

    def execute_test(self):
        unittest.main(
            module=__name__,
            argv=[""],
            defaultTest=f"{StackTester.__name__}.{StackTester.TestStackContainer.__name__}",
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


class QueueTester(Tester):
    class TestQueueContainer(unittest.TestCase):
        longMessage = True

    def __init__(self) -> None:
        super().__init__()
        self.methods: dict[str, tuple[int, int]] = {
            "__init__": (1, 0),
            "enqueue": (1, 0),
            "dequeue": (0, 1),
            "is_empty": (0, 1),
            "is_full": (0, 1),
        }

    def create_tests(self, queueClass: Any) -> list[Callable]:
        def test_is_empty(self: unittest.TestCase):
            q = queueClass(10)
            self.assertTrue(q.is_empty())

        def test_is_full(self: unittest.TestCase):
            n = 10
            q = queueClass(n)
            for i in range(n):
                q.enqueue(i)

            self.assertTrue(q.is_full(), "deberia estar llena luego de insertar elementos hasta el maximo de capacidad")
            self.assertFalse(q.is_empty(), "no deberia reportar que esta vacia cuando esta llena")

        def test_enqueue_dequeue(self: unittest.TestCase):
            from random import randint

            n = randint(300, 1000)
            q = queueClass(n)
            self.assertTrue(q.is_empty())
            for i in range(n):
                self.assertFalse(q.is_full(), f"la cola tiene capacidad {n}, pero se lleno con {i+1} elementos")
                q.enqueue(i)
            self.assertTrue(q.is_full(), "la cola debe estar llena al insertarse una cantidad de elementos iguales a su capacidad")

            expectedValue = 0
            count = 0
            while not q.is_empty() and count < n:
                gotValue = q.dequeue()
                self.assertEqual(expectedValue, gotValue, "se esperaba un valor diferente al desencolar")
                expectedValue += 1
                count += 1

            self.assertTrue(count != n or q.is_empty(), "la cola deberia estar vacia despues de sacar todos los elementos que estan dentro")

        def test_dequeue_fail_if_empty(self: unittest.TestCase):
            q = queueClass(10)
            with self.assertRaises(AssertionError, msg="debe fallar si se desencola sobre una cola vacia"):
                q.dequeue()

        def test_enqueue_fail_if_full(self: unittest.TestCase):
            n = 10
            q = queueClass(n)
            for i in range(n):
                self.assertFalse(q.is_full())
                q.enqueue(i)
            self.assertTrue(q.is_full())

            with self.assertRaises(AssertionError, msg="debe fallar si se intenta encolar una cola llena"):
                q.enqueue(None)

        def test_should_fail_on_invalid_size(self: unittest.TestCase):
            with self.assertRaises(AssertionError, msg="deberia fallar al inicializar la cola con un tamaño invalido"):
                queueClass(0)

            with self.assertRaises(AssertionError, msg="deberia fallar al inicializar la cola con un tamaño invalido"):
                queueClass(-1)

        return [
            test_is_empty,
            test_is_full,
            test_enqueue_dequeue,
            test_dequeue_fail_if_empty,
            test_enqueue_fail_if_full,
            test_should_fail_on_invalid_size,
        ]

    def setup_tests(self, obj: Any):
        tests = self.create_tests(obj)
        for test in tests:
            name = test.__name__
            setattr(QueueTester.TestQueueContainer, name, test)

    def execute_test(self):
        unittest.main(
            module=__name__,
            argv=[""],
            defaultTest=f"{QueueTester.__name__}.{QueueTester.TestQueueContainer.__name__}",
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

class LinkedListTester(Tester):
    class TestLinkedListContainer(unittest.TestCase):
        longMessage = True

    def __init__(self) -> None:
        super().__init__()
        self.methods: dict[str, tuple[int, int]] = {
            "__init__": (0, 0),
            "prepend": (1, 0),
        }

    def create_tests(self, llClass: Any) -> list[Callable]:
        def test_invert(self: unittest.TestCase):
            ll = llClass()
            if not hasattr(ll, "invert"):
                self.skipTest("skipped")

            n = 100
            for i in range(n):
                ll.prepend(i)

            ll.invert()
            curr = ll.nil.next
            values = []
            while curr is not ll.nil:
                values.append(curr.key)
                curr = curr.next

            self.assertTrue(all(values[i] < values[i+1] for i in range(len(values)-1)), "los valores de la lista deben estar invertidos")

        def test_remove_duplicates(self: unittest.TestCase):
            ll = llClass()
            if not hasattr(ll, "remove_duplicates"):
                self.skipTest("skipped")

            n = 100
            for i in range(1, n+1):
                for _ in range(i):
                    ll.prepend(i)

            ll.remove_duplicates()

            curr = ll.nil.next
            values = []
            while curr is not ll.nil:
                values.append(curr.key)
                curr = curr.next

            self.assertEqual(n, len(values), "deberia remover los duplicados de la lista")
            values = set(values)
            for i in range(1, n):
                self.assertTrue(i in values, "todos los elementos unicos deben estar dentro de la lista al menos una vez")

        def test_union(self: unittest.TestCase):
            l1 = llClass()
            l2 = llClass()
            if not hasattr(l1, "union"):
                self.skipTest("skipped")

            na = 100
            nb = 50
            for _ in range(na):
                l1.prepend("A")

            for _ in range(nb):
                l2.prepend("B")

            l1.union(l2)

            curr = l1.nil.next
            values = []
            while curr is not l1.nil:
                values.append(curr.key)
                curr = curr.next

            self.assertEqual(na + nb, len(values), "la cantidad de elementos en la primera cola debe ser ahora la suma de ambas listas")
            d: dict[str, int] = {}
            for v in values:
                d[v] = d.get(v, 0) + 1

            self.assertEqual(d.get("A", 0), na)
            self.assertEqual(d.get("B", 0), nb)

        return [
            test_invert,
            test_remove_duplicates,
            test_union,
        ]

    def setup_tests(self, obj: Any):
        tests = self.create_tests(obj)
        for test in tests:
            name = test.__name__
            setattr(LinkedListTester.TestLinkedListContainer, name, test)

    def execute_test(self):
        unittest.main(
            module=__name__,
            argv=[""],
            defaultTest=f"{LinkedListTester.__name__}.{LinkedListTester.TestLinkedListContainer.__name__}",
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

class QueueLLTester(Tester):
    class TestQueueContainer(unittest.TestCase):
        longMessage = True

    def __init__(self) -> None:
        super().__init__()
        self.methods: dict[str, tuple[int, int]] = {
            "__init__": (0, 0),
            "enqueue": (1, 0),
            "dequeue": (0, 1),
            "is_empty": (0, 1),
        }

    def create_tests(self, queueClass: Any) -> list[Callable]:
        def test_is_empty(self: unittest.TestCase):
            q = queueClass()
            self.assertTrue(q.is_empty())

        def test_enqueue_dequeue(self: unittest.TestCase):
            from random import randint

            n = randint(300, 1000)
            q = queueClass()
            self.assertTrue(q.is_empty())
            for i in range(n):
                q.enqueue(i)

            expectedValue = 0
            count = 0
            while not q.is_empty() and count < n:
                gotValue = q.dequeue()
                self.assertEqual(expectedValue, gotValue, "se esperaba un valor diferente al desencolar")
                expectedValue += 1
                count += 1

            self.assertTrue(count != n or q.is_empty(), "la cola deberia estar vacia despues de sacar todos los elementos que estan dentro")

        def test_dequeue_fail_if_empty(self: unittest.TestCase):
            q = queueClass()
            with self.assertRaises(AssertionError, msg="debe fallar si se desencola sobre una cola vacia"):
                q.dequeue()

        return [
            test_is_empty,
            test_enqueue_dequeue,
            test_dequeue_fail_if_empty,
        ]

    def setup_tests(self, obj: Any):
        tests = self.create_tests(obj)
        for test in tests:
            name = test.__name__
            setattr(QueueLLTester.TestQueueContainer, name, test)

    def execute_test(self):
        unittest.main(
            module=__name__,
            argv=[""],
            defaultTest=f"{QueueLLTester.__name__}.{QueueLLTester.TestQueueContainer.__name__}",
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
            "stack": StackTester(),
            "queue": QueueTester(),
            "linkedlist_invert": LinkedListTester(),
            "linkedlist_removeduplicates": LinkedListTester(),
            "linkedlist_union": LinkedListTester(),
            "linkedlist_queue": QueueLLTester(),
        }

    def grade(self, part: str, answer: Any):
        if part not in self.testers:
            banner(Fore.RED + "ERROR: codigo de ejercicio es invalido :clown_face:")
            return

        tester = self.testers[part]
        tester.check(answer)
