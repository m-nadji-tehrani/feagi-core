


def genome_stats_analytics(test_stats):
    exposure_total = 0
    comprehended_total = 0
    for test in test_stats:
        for key in test:
            if "exposed" in key:
                exposure_total += test[key]
            if "comprehended" in key:
                comprehended_total += test[key]

    return exposure_total, comprehended_total


def calculate_fitness(test_stats):
    """
    Calculate the effectiveness of a given genome:
    1. Fitness value will be a number between 0 and 100 with 100 the highest fitness possible (how can there be limit?)
    2. Brain activeness should be considered as a factor. Brain that only guessed one number and that one correctly
          should not be considered better than a brain that guessed 100s of numbers 95% correct.
    3. Number of guess attempts vs. number of correct guesses is a factor

    Fitness calculation formula:

    TE = Total number of times brain has been exposed to a character
    TC = Total number of times brain has comprehended a number correctly
    AF = Activity factor that is measured by a threshold.
        - < 10 exposures leads to 0
        - > 10 & < 50 exposures leads to n / 50 factor
        - > 50 exposures leads to 1

    TC / TE = Percentage of correct comprehensions

    Genome fitness factor = AF * TC / TE

    """
    total_exposure, total_comprehended = genome_stats_analytics(test_stats)

    if total_exposure < 10:
        activity_factor = 0
    elif 10 <= total_exposure <= 50:
        activity_factor = total_exposure / 50
    else:
        activity_factor = 1

    fitness = activity_factor * total_comprehended / total_exposure

    return fitness

test_stats = [{'genome_id': '2018-06-26_10:46:32_947229_G1FG6A_G', 'test_id': '2018-06-26_10:47:36_405664_KRIAGT_T', '1_exposed': 3, '1_comprehended': 3}, {'genome_id': '2018-06-26_10:46:32_947229_G1FG6A_G', 'test_id': '2018-06-26_10:47:54_598120_SATPC2_T', '2_exposed': 300, '2_comprehended': 300}, {'genome_id': '2018-06-26_10:46:32_947229_G1FG6A_G', 'test_id': '2018-06-26_10:48:10_671141_Q1IN1X_T', '2_exposed': 3, '2_comprehended': 3}, {'genome_id': '2018-06-26_10:46:32_947229_G1FG6A_G', 'test_id': '2018-06-26_10:48:26_086441_5D6A93_T', '3_exposed': 3, '3_comprehended': 3}, {'genome_id': '2018-06-26_10:46:32_947229_G1FG6A_G', 'test_id': '2018-06-26_10:48:56_636572_SPGHSK_T', '4_exposed': 3, '4_comprehended': 3}]


print(calculate_fitness(test_stats))