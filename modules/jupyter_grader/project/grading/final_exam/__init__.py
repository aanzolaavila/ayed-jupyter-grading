import contextlib
from typing import Any, Callable, TextIO
from ..types import Checker
from abc import ABC, abstractmethod
import inspect
from ..utils import banner
from colorama import Fore
import unittest
import types
import time
import multiprocessing
import sys
import os
import tempfile
import logging
from queue import Empty

logger = logging.getLogger(__name__)


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
        if type(method) is types.FunctionType:
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


async def async_main(function, timeout: int | float):
    e = None
    banner(
        Fore.CYAN
        + "[RUNTIME ERROR]"
        + Fore.MAGENTA
        + " - Su codigo saco una excepcion: "
        + Fore.LIGHTBLACK_EX
        + f"{e}"
    )
    banner(
        Fore.RED
        + "[TIME LIMIT]"
        + Fore.MAGENTA
        + f" - su codigo llego al tiempo permitido ({timeout}s)"
    )
    raise


class ExamGrader(Tester):
    class TestExamContainer(unittest.TestCase):
        longMessage = True

    def __init__(self, problem: str, timeout: int | float) -> None:
        super().__init__()
        self.problem = problem
        self.timeout = timeout

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

        return [
            test_preorder_tree_walk,
        ]

    def setup_tests(self, obj: Any):
        tests = self.create_tests(obj)
        for test in tests:
            name = test.__name__
            setattr(ExamGrader.TestExamContainer, name, test)

    def execute_test(self):
        unittest.main(
            module=__name__,
            argv=[""],
            defaultTest=f"{ExamGrader.__name__}.{ExamGrader.TestExamContainer.__name__}",
            verbosity=2,
            exit=False,
        )

    def check(self, obj: Any):
        # if not isinstance(main, Callable):
        #     banner(
        #         Fore.RED
        #         + f"Debe proveer la funcion del problema a tratar"
        #     )
        #     return
        logger.debug("Type object", extra={"type": type(obj)})

        main: Callable = obj

        def main_wrapper(
            infile: TextIO, outfile: TextIO, exceptionQueue: multiprocessing.Queue
        ):
            sys.stdin = infile

            def custom_input(prompt: str = "") -> str:
                print(prompt, file=outfile, flush=True, end="")
                s = infile.readline().strip()
                return s

            try:
                with contextlib.redirect_stdout(outfile):
                    main(infile, custom_input)
                    sys.stdout.flush()
            except Exception as e:
                exceptionQueue.put(e)

        # self.setup_tests(obj)

        problem_dir = (
            os.path.dirname(os.path.realpath(__file__)) + "/problems/" + self.problem
        )

        testcases = [f[:-3] for f in os.listdir(problem_dir) if f.endswith(".in")]

        banner(Fore.LIGHTBLACK_EX + f"Problema {self.problem}" + Fore.BLACK)
        times = []
        for case in testcases:
            banner(Fore.LIGHTBLACK_EX + f"Ejecutando caso {case}" + Fore.BLACK)

            infile = open(f"{problem_dir}/{case}.in")
            outcapture = tempfile.NamedTemporaryFile(mode="w", delete=False)
            exceptionQueue = multiprocessing.Queue()
            p = multiprocessing.Process(
                target=main_wrapper,
                args=(infile, outcapture, exceptionQueue),
                name=(f"{self.problem}_{case}"),
            )
            p.start()

            start_time = time.time()
            while time.time() - start_time <= self.timeout and p.is_alive():
                time.sleep(0.1)

            end_time = time.time()
            delta = end_time - start_time
            times.append(delta)
            infile.close()
            outcapture.close()

            if p.is_alive():
                p.terminate()
                banner(
                    Fore.BLUE
                    + "[TIME LIMIT]"
                    + Fore.MAGENTA
                    + f" - su programa llego al tiempo límite permitido ({self.timeout:.2f}s)"
                    + Fore.BLACK
                )
                return

            exception: Exception | None = None
            try:
                exception = exceptionQueue.get_nowait()
            except Empty:
                pass
            exceptionQueue.close()
            if exception:
                logger.debug("got exception: %s", exception)
                banner(
                    Fore.CYAN
                    + "[RUNTIME ERROR]"
                    + Fore.MAGENTA
                    + " - Su programa lanzó una excepción: "
                    + Fore.LIGHTBLACK_EX
                    + f"{exception}"
                )
                return

            # Compare outputs
            with open(f"{problem_dir}/{case}.out", "r") as outfile:
                expected_out = outfile.readlines()
            with open(outcapture.name, "r") as outfile:
                got_out = outfile.readlines()

            logger.debug(
                "Program output expected: %s vs got: %s", expected_out, got_out
            )

            equal = compare_outputs(expected_out, got_out)
            if not equal:
                banner(Fore.RED + "[WRONG ANSWER]" + Fore.BLACK + f" ({delta:.2f}s)")
                return

            banner(
                Fore.LIGHTBLACK_EX + f"Terminado caso {case}: {delta:.2f}s" + Fore.BLACK
            )

        banner(
            Fore.GREEN
            + "[ACCEPTED]"
            + Fore.LIGHTBLACK_EX
            + f" ({sum(times):.2f}s/{self.timeout}s)"
            + Fore.BLACK
        )

        # self.execute_test()


def clean_str(s: str) -> str:
    return s.strip("\n")


def compare_outputs(expected_lines: list[str], got_lines: list[str]) -> bool:
    if len(expected_lines) != len(got_lines):
        return False
    expected_map = map(clean_str, expected_lines)
    got_map = map(clean_str, got_lines)
    for expected, got in zip(expected_map, got_map):
        if expected != got:
            logger.debug("Got differences expected: %s vs got: %s", expected, got)

            return False
    return True


class Grader(Checker):
    def __init__(self, name: str, code: int, debug: bool = False) -> None:
        super().__init__(name, code)
        self.testers: dict[str, Tester] = self.get_testers()
        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.CRITICAL)

    def get_testers(self) -> dict[str, Tester]:
        return {
            "example": ExamGrader("example", 1.0),
            "A": ExamGrader("A", 2.0),
            "B": ExamGrader("B", 2.0),
            "C": ExamGrader("C", 5.0),
        }

    def grade(self, part: str, answer: Any):
        if part not in self.testers:
            banner(
                Fore.RED
                + "ERROR: codigo de ejercicio es invalido :clown_face:"
                + f": se obtuvo {part}, se esperaba uno de {self.testers.keys()}"
            )
            return

        tester = self.testers[part]
        tester.check(answer)
