credential = input()


    if int(prob_num) in range(0, 4):
        solutions = os.listdir(f"problems/{prob_num}/solutions")
        testcases = os.listdir(f"problems/{prob_num}/testcases")
        solutions.sort()
        testcases.sort()
    else:
        raise Exception("problem number error")