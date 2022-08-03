import os
import subprocess
import random ## test
from datetime import datetime ## test

class RuntimeError(Exception):
    pass

class CompileError(Exception):
    pass

class TimeoutError(Exception):
    pass

class WrongImplementation(Exception):
    pass

class InternalServerError(Exception):
    pass


def _get_random(a, b): # inclu-inclu
    random.seed(str(datetime.now()))
    random_num = random.randint(a,b)
    return random_num

def _get_free_container():
    get_cont_proc = subprocess.Popen('sudo docker stats --no-stream --format "{{.Container}}:{{.CPUPerc}}"', shell=True, stdout=subprocess.PIPE)
    get_cont_proc.wait()
    try:
        out, err = get_cont_proc.communicate()
        to_str = (out.decode()).strip()
        container_list=to_str.split("\n")
        rand_idx = _get_random(0, len(container_list)-1)

        result_container = ""
        while(True):
            [container_id, cpu_info_str] = container_list[rand_idx].split(":") # ex) 39.00%
            cpu_info_int = int(cpu_info_str[:-4])
            if cpu_info_int<50:
                result_container=container_id
                break      
            rand_idx=_get_random(0, len(container_list)-1)
        return True, result_container
    except Exception as e:
        return False, str(e)

def _add_user(user_id, container_id):
    #권한 제거된 사용자 추가
    adduser_proc = subprocess.Popen(f"bash ./scripts/add_user.sh {user_id} {container_id}", shell=True)    
    adduser_proc.wait()
    adduser_proc.communicate()
    return

def _del_user(user_id, container_id):
    # #사용자 및 폴더 제거
    deluser_proc = subprocess.Popen(f"bash ./scripts/del_user.sh {user_id} {container_id}", shell=True)
    deluser_proc.wait()
    deluser_proc.communicate()
    return


def solve(language, user_id, prob_num):

    file_path = f"codes/{user_id}/{prob_num}/"

    if int(prob_num) in range(0, 4):
        solutions = os.listdir(f"problems/{prob_num}/solutions")
        testcases = os.listdir(f"problems/{prob_num}/testcases")
        solutions.sort()
        testcases.sort()
    else:
        raise InternalServerError("problem number error")

    # Compile if needed
    if language == "java":
        compile_proc = subprocess.Popen(f"javac {file_path}*.java -d {file_path} -nowarn", shell=True, stderr=subprocess.PIPE)
        compile_proc.wait()
        outs, errs = compile_proc.communicate()
        if errs:
            print(errs)
            raise CompileError("컴파일 에러")
    
    elif language == "kotlin":
        compile_proc = subprocess.Popen(f"kotlinc-jvm {file_path}*.kt -include-runtime -d {file_path}main.jar -nowarn", shell=True,
                                        stderr=subprocess.PIPE)
        compile_proc.wait()
        outs, errs = compile_proc.communicate()
        if errs:
            print(errs)
            raise CompileError("컴파일 에러")

    elif language == "c++":
        print("CPP CAME!!")
        compile_proc = subprocess.Popen(f"g++ -std=c++11 {file_path}*.cpp -o {file_path}main.out", shell=True, stderr=subprocess.PIPE)
        compile_proc.wait()
        outs, errs = compile_proc.communicate()
        language = "cpp"
        if errs:
            print(errs)
            raise CompileError("컴파일 에러")
    


    container_selected, container_id = _get_free_container()
    if not container_selected:
        print(container_id)
        raise InternalServerError("container not selected")
    
    print(f"{container_id}에서 시작합니다.")
    _add_user(user_id, container_id)

    for test_case_filename, solution_filename in zip(testcases, solutions):

        # get answer from user
        runtest_proc = subprocess.Popen(f"bash ./scripts/run_test.sh {user_id} {prob_num} {language} {test_case_filename} {container_id}", shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)    
    
        try:
            outs, errs = runtest_proc.communicate(timeout=1.1)
        except subprocess.TimeoutExpired:
            runtest_proc.kill()
            _del_user(user_id, container_id)
            raise TimeoutError("시간 초과")            
        except Exception as e:
            runtest_proc.kill()
            print(e)
            _del_user(user_id, container_id)
            raise RuntimeError("런타임 에러")
        if errs:
            print(f"{test_case_filename}에서 발생함 ㅇㅇ")
            print(errs.decode())
            _del_user(user_id, container_id)
            raise RuntimeError("런타임 에러")

        solution_file = open(f"problems/{prob_num}/solutions/{solution_filename}", "r")
        solution = solution_file.read()
        solution_file.close()
        out = outs.decode()
        print("사용자의 답, ", out.rstrip('\n'))
        print("정답, ", solution.rstrip('\n'))
        if out.strip() != solution.strip():
            raise WrongImplementation("오답")
        print(f"{test_case_filename} 맞았삼")

    _del_user(user_id, container_id) 

    return True
