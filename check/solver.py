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

##############################
## UNDER CONSTRUCTION ########
##############################

def solve(language, user_id, prob_num):

    file_path = f"codes/{user_id}/{prob_num}/"
    print("file path: " + file_path)
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
            raise CompileError(errs.decode())

    elif language == "kotlin":
        compile_proc = subprocess.Popen(f"kotlinc {file_path}*.kt -include-runtime -d {file_path}main.jar -nowarn", shell=True,
                                        stderr=subprocess.PIPE)
        compile_proc.wait()
        outs, errs = compile_proc.communicate()
        if errs:
            raise Exception(f"compile error: {errs.decode()}")

    # [TODO] add c++
    # (daeyong) 임시방편으로 ts를 cpp로 바꿔서 실행중
    elif language == "typescript":
        compile_proc = subprocess.Popen(f"gcc {file_path}*.cpp -o {file_path}main.out -lstdc++", shell=True, stderr=subprocess.PIPE)
        compile_proc.wait()
        outs, errs = compile_proc.communicate()
        if errs:
            raise Exception(f"compile error: {errs.decode()}")


    #권한 제거된 사용자 추가
    adduser_proc = subprocess.Popen(["bash", "./scripts/add_user.sh"])
    adduser_proc.wait()
    outs, errs = adduser_proc.communicate()

    print(outs)

    for test_case_filename, solution_filename in zip(testcases, solutions):
        runtest_proc = subprocess.Popen(["bash", "./scripts/run_test.sh", user_id, prob_num, language, test_case_filename])

        solution_file = open(f"problems/{prob_num}/solutions/{solution_filename}", "r")

        try:
            outs, errs = runtest_proc.communicate(timeout=1.1)
        except subprocess.TimeoutExpired:
            runtest_proc.kill()
            raise TimeoutError("시간 초과")
        except Exception as e:
            runtest_proc.kill()
            raise Exception("Server error")
        if errs:
            raise RuntimeError(errs.decode())

        solution = solution_file.read()
        solution_file.close()
        out = outs.decode()
        if out.rstrip('\n') != solution.rstrip('\n'):
            raise Exception(out)

        return True

    # # #사용자 및 폴더 제거
    # deluser_proc = subprocess.Popen(["bash", "./scripts/del_user.sh"])
    # deluser_proc.wait()

    # return True
