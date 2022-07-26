from sqlite3 import Time
from waffle_recruit_server.celery import app
from .solver import solve
from .solver import RuntimeError, CompileError, WrongImplementation, InternalServerError, TimeoutError
from pathlib import Path

root_path = str(Path(__file__).parent.parent.resolve())


@app.task(name='solver')
def run_solver(language, user_id, prob_num):

    try:
        solve(language, user_id, prob_num)
        return True, prob_num, {}
    except RuntimeError as e:
        return False, prob_num, {"error": "Runtime error"}
    except CompileError as e:
        return False, prob_num, {"error": "Compile error"}
    except TimeoutError as e:
        return False, prob_num, {"error": "Timeout error"}
    except WrongImplementation as e:
        return False, prob_num, {"error": "Wrong implementation"}
    except InternalServerError as e:
        return False, prob_num, {"error": "Interal server error"} 
    except Exception as e:
        return False, prob_num, {"error": "Wrong implementation"}
