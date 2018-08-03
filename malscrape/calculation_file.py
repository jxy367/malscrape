def expected_number_of_users(max_value, ratio, num_spiders, total_parts):
    return round(spider_total_users(max_value, ratio, num_spiders)*multiplier_calculation(ratio, total_parts - 1))


def multiplier_calculation(ratio, number):
    return sub_multiplier_calculation(0, ratio, number)


def sub_multiplier_calculation(current_multiplier, ratio, number):
    if number < 0:
        return current_multiplier
    else:
        return sub_multiplier_calculation(current_multiplier + ratio**number, ratio, number - 1)


def spider_total_users(max_value, ratio, num_spiders):
    return round(max_value * multiplier_calculation(ratio, num_spiders-1))


expected_max_value = 420000
current_ratio = 0.13
num_spiders = 3
parts = 30

print("Expected number of users: " + str(expected_number_of_users(expected_max_value, current_ratio, num_spiders, parts)))
print("Expected spider total users: " + str(spider_total_users(expected_max_value, current_ratio, num_spiders)))
