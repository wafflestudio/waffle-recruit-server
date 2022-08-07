from sqlite3 import Time
from waffle_recruit_server.celery import app
from .solver import solve
from .solver import RuntimeError, CompileError, WrongImplementation, InternalServerError, TimeoutError
from pathlib import Path

root_path = str(Path(__file__).parent.parent.resolve())


@app.task(name='solver')
def run_solver(language, user_id, prob_num):
    # if prob_num == 0:
    #     return False, prob_num, {"err_code": 1, "err_msg": "Runtime error"}
    # return True, prob_num, {}

    try:
        solve(language, user_id, prob_num)
        return True, prob_num, {}
    except RuntimeError as e:
        return False, prob_num, {"err_code": 1, "err_msg": "Runtime error"}
    except CompileError as e:
        return False, prob_num, {"err_code": 2, "err_msg": "Compile error"}
    except TimeoutError as e:
        print("task.py로 옴 ㅎ")
        return False, prob_num, {"err_code": 3, "err_msg": "Timeout error"}
    except WrongImplementation as e:
        return False, prob_num, {"err_code": 4, "err_msg": "Wrong implementation"}
    except InternalServerError as e:
        return False, prob_num, {"err_code": 5, "err_msg": "Interal server error"} 
    except Exception as e:
        print(e.decode())
        return False, prob_num, {"err_code": 4, "err_msg": "Wrong implementation"}
