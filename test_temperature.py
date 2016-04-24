# Run with
# python -m pytest test_temperature.py
import temperature

W1_OUTPUT_TEST_FILE = temperature.HOME_DIR + 'w1_output.txt'
W1_TEST_OUTPUT = ''
with open(W1_OUTPUT_TEST_FILE, 'r') as f:
    W1_TEST_OUTPUT = f.read()


def test_get_temp():
    assert temperature.get_temp_from_w1_data(W1_TEST_OUTPUT) == 18.937 - temperature.T_CALIBRATION


def test_is_temp_ok():
    dT = 0.1
    assert temperature.is_temp_ok(temperature.T_MAX - dT) == True
    assert temperature.is_temp_ok(temperature.T_MIN + dT) == True
    assert temperature.is_temp_ok(temperature.T_MAX + dT) == False
    assert temperature.is_temp_ok(temperature.T_MIN - dT) == False