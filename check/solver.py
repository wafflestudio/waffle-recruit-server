import os
import subprocess


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



def _add_user(user_id):
    #권한 제거된 사용자 추가
    adduser_proc = subprocess.Popen(f"bash ./scripts/add_user.sh {user_id}", shell=True)    
    adduser_proc.wait()
    adduser_proc.communicate()
    return

def _del_user(user_id):
    # #사용자 및 폴더 제거
    deluser_proc = subprocess.Popen(f"bash ./scripts/del_user.sh {user_id}", shell=True)
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
        raise Exception("problem number error")


    # Compile if needed
    if language == "java":
        compile_proc = subprocess.Popen(f"javac {file_path}*.java -d {file_path} -nowarn", shell=True, stderr=subprocess.PIPE)
        compile_proc.wait()
        outs, errs = compile_proc.communicate()
        if errs:
            print(errs) 
            raise CompileError("컴파일 에러")

    elif language == "kotlin":
        compile_proc = subprocess.Popen(f"kotlinc {file_path}*.kt -include-runtime -d {file_path}main.jar -nowarn", shell=True,
                                        stderr=subprocess.PIPE)
        compile_proc.wait()
        outs, errs = compile_proc.communicate()
        if errs:
            raise CompileError("컴파일 에러")

    # [TODO] add c++
    # (daeyong) 임시방편으로 ts를 cpp로 바꿔서 실행중
    elif language == "typescript":
        # compile_proc = subprocess.Popen(f"gcc {file_path}*.cpp -o {file_path}main.out -lstdc++", shell=True, stderr=subprocess.PIPE)
        compile_proc = subprocess.Popen(f"gcc {file_path}*.cpp -o {file_path}main.out", shell=True, stderr=subprocess.PIPE)

        compile_proc.wait()
        outs, errs = compile_proc.communicate()
        if errs:
            raise CompileError("컴파일 에러")

    _add_user(user_id)

    for test_case_filename, solution_filename in zip(testcases, solutions):

        # get answer from user
        runtest_proc = subprocess.Popen(f"bash ./scripts/run_test.sh {user_id} {prob_num} {language} {test_case_filename}", shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)    
    
        try:
            outs, errs = runtest_proc.communicate(timeout=1.1)
        except subprocess.TimeoutExpired:
            runtest_proc.kill()
            _del_user(user_id)
            raise TimeoutError("시간 초과")            
        except Exception as e:
            runtest_proc.kill()
            _del_user(user_id)
            raise RuntimeError("런타임 에러")
        if errs:
            _del_user(user_id)
            raise RuntimeError("런타임 에러")

        solution_file = open(f"problems/{prob_num}/solutions/{solution_filename}", "r")
        solution = solution_file.read()
        solution_file.close()
        out = outs.decode()
        print(f"사용자의 답 [{out}]")
        if out.rstrip('\n') != solution.rstrip('\n'):
            raise WrongImplementation("오답")
        print(f"{test_case_filename} 맞았삼")

    _del_user(user_id) 

    return True
