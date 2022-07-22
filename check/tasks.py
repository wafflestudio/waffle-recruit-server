from waffle_recruit_server.celery import app
from .solver import solve
from .solver import RuntimeError, CompileError
from pathlib import Path

root_path = str(Path(__file__).parent.parent.resolve())


@app.task(name='solver')
def run_solver(language, file_path, prob_num):
    return True, prob_num, {}


    #### UNDER CONSTRUCTION ####

    # try:
    #     solve(language, file_path, prob_num)
    #     return True, prob_num, {}
    # except RuntimeError as e:
    #     return False, prob_num, {"error": "Runtime error", "detail": str(e).replace(root_path, "").replace(file_path, "submission/")}
    # except CompileError as e:
    #     return False, prob_num, {"error": "Compile error", "detail": str(e).replace(root_path, "").replace(file_path, "submission/")}
    # except Exception as e:
    #     return False, prob_num, {"error": "Wrong solution", "detail": str(e).replace(root_path, "").replace(file_path, "submission/")}
