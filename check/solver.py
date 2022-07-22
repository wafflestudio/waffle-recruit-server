import os
import subprocess


class RuntimeError(Exception):
    pass


class CompileError(Exception):
    pass


##############################
## UNDER CONSTRUCTION ########
##############################

def solve(user_cred, language, file_path, prob_num):
    print("file path: " + file_path)
    if int(prob_num) in range(0, 4):
        solutions = os.listdir(f"problems/{prob_num}/solutions")
        testcases = os.listdir(f"problems/{prob_num}/testcases")
        solutions.sort()
        testcases.sort()
    else:
        raise Exception("problem number error")

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

    # elif language == "typescript":
    #     compile_proc = subprocess.Popen(f"tsc {file_path}*.ts", shell=True,
    #                                     stderr=subprocess.PIPE)
    #     compile_proc.wait()
    #     outs, errs = compile_proc.communicate()
    #     if errs:
    #         raise Exception(f"compile error: {errs.decode()}")


    #권한 제거된 사용자 추가
    subprocess.Popen(["bash", "../scripts/add_user.sh"])
    
    for test_case_filename, solution_filename in zip(testcases, solutions):
        proc = subprocess.Popen(["bash", "../scripts/run_test.sh", user_cred, prob_num, language, test_case_filename])

        # test_case = open(f"problems/{prob_num}/testcases/{test_case_filename}", "r")
        solution_file = open(f"problems/{prob_num}/solutions/{solution_filename}", "r")
        kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            # "stdin": test_case,
        }

        ## below is now scripted

        else:
            raise Exception("language error")
        try:
            outs, errs = proc.communicate(timeout=1.1)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise Exception("시간 초과")
        except Exception as e:
            proc.kill()
            raise Exception("Server error")
        if errs:
            raise RuntimeError(errs.decode())

        solution = solution_file.read()
        # test_case.close()
        solution_file.close()
        out = outs.decode()
        if out.rstrip('\n') != solution.rstrip('\n'):
            raise Exception(out)

    #사용자 및 폴더 제거
    subprocess.Popen(["bash", "../scripts/del_user.sh"])


    return True
