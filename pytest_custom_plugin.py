# pytest_custom_plugin.py

def pytest_html_results_table_html(report, data):
    if report.passed:
        for item in report.items:
            if hasattr(item, "callspec"):
                callspec = item.callspec
                parameters = getattr(callspec, "params", {})
                test_parameters = ", ".join(f"{key}={value}" for key, value in parameters.items())
                data.append(("Test Parameters", test_parameters))

                # Custom modification to include values used in tests
                test_function = item.function.__name__
                if test_function.startswith("test_"):
                    test_name = test_function[5:].replace("_", " ").capitalize()
                    test_code = item.function.__code__.co_code  # Get bytecode of the test function
                    test_consts = item.function.__code__.co_consts  # Get constants used in the test function
                    test_values = []
                    for i, const in enumerate(test_consts):
                        if const == "grade_input.send_keys":
                            value = test_consts[i + 1]  # Get the value used with send_keys
                            test_values.append(str(value))
                    if test_values:
                        test_values_str = ", ".join(test_values)
                        data.append(("Test Values", f"{test_name}: {test_values_str}"))
