import time
import traceback
import os
import pandas as pd

class InvalidDSLUsageError(Exception):
    def __init__(self, message="Invalid DSL usage"):
        super().__init__(message)

class InvalidObjectUsageError(InvalidDSLUsageError):
    def __init__(self, message="Invalid object usage in DSL", object=None, objects=None):
        super().__init__(message + f"\n\n object: {object}, objects: {objects}")

class InvalidPixelUsageError(InvalidDSLUsageError):
    def __init__(self, message="Invalid pixcel usage in DSL", r=None, c=None, grid_r_size=None, grid_c_size=None):
        super().__init__(message + f"\n\n r: {r}, c: {c}\n\n grid_r_size: {grid_r_size}, grid_c_size: {grid_c_size}")

class NonExistentDSLError(InvalidDSLUsageError):
    def __init__(self, message="Non-existent DSL name", dsl=None):
        super().__init__(message + f"\n\n dsl: {dsl}")

class NonExistentColorError(InvalidDSLUsageError):
    def __init__(self, message="Non-existent color type", color=None):
        super().__init__(message + f"\n\n color: {color}")

class DSLInternalLogicError(Exception):
    def __init__(self, message="Internal logic error in DSL function", dsl=None, object=None, objects=None, color=None, r1=None, c1=None, r2=None, c2=None, grid_r_size=None, grid_c_size=None, state=None):
        super().__init__(message + f"\n\n dsl: {dsl}, \n\nobject: {object}, \n\nobjects: {objects}, \n\ncolor: {color}, r1: {r1}, c1: {c1}, \n\nr2: {r2}, c2: {c2}, \n\ngrid_r_size: {grid_r_size}, grid_c_size: {grid_c_size}, \n\nstate: {state}")

class ParseError(Exception):
    def __init__(self, message="Parse error about the LLM output"):
        super().__init__(message)

def check_pixel(state, r, c):
    if r < 0 or c < 0:
        raise InvalidPixelUsageError(r=r, c=c, grid_r_size=len(state), grid_c_size=len(state[0]))
    if r >= len(state) or c >= len(state[0]):
        raise InvalidPixelUsageError(r=r, c=c, grid_r_size=len(state), grid_c_size=len(state[0]))

def check_color(color):
    if color not in [i for i in range(10)]:
        raise NonExistentColorError(color=color)

def check_object(object, objects):
    if object not in objects.keys():
        raise InvalidObjectUsageError(object=object, objects=objects)

def save_exception_log(e, problem_index, problem_id, except_error_csv_file_path,
                       InvalidObjectUsageError_flag, NonExistentDSLError_flag, DSLInternalLogicError_flag,
                       InvalidDSLUsageError_flag, InvalidPixelUsageError_flag, NonExistentColorError_flag,
                       ParseError_flag, ExceptionError_flag):
    print(f"Error: {problem_index}")
    print(e)

    except_time = time.time()
    except_local_time = time.localtime(except_time)
    format_except_local_time = time.strftime('%Y-%m-%d %H:%M:%S', except_local_time)

    except_error_log_data = {
        "problem": [problem_index],
        "problem_id": [problem_id],
        "error": [str(e)],
        "error_traceback": [traceback.format_exc()],
        "invalid_object_usage_error": [InvalidObjectUsageError_flag],
        "non_existent_dsl_error": [NonExistentDSLError_flag],
        "dsl_internal_logic_error": [DSLInternalLogicError_flag],
        "invalid_dsl_usage_error": [InvalidDSLUsageError_flag],
        "invalid_pixel_usage_error": [InvalidPixelUsageError_flag],
        "non_existent_color_error": [NonExistentColorError_flag],
        "parse_error": [ParseError_flag],
        "exception_error": [ExceptionError_flag],
        "time": [format_except_local_time],
    }

    df_except_error = pd.DataFrame(except_error_log_data)

    if not os.path.isfile(except_error_csv_file_path):
        df_except_error.to_csv(except_error_csv_file_path, index=False)
    else:
        df_except_error.to_csv(except_error_csv_file_path, mode='a', header=False, index=False)
