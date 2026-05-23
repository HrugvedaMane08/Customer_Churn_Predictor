import sys

def error_message_detail(error, error_detail: sys):
    """
    Formulate a detailed error message displaying the python script name, 
    line number, and the exact error description.
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = f"Error occurred in python script name [{file_name}] line number [{line_number}] error message [{str(error)}]"
    return error_message

class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail=error_detail)

    def __str__(self):
        return self.error_message

# Example usage/tester block
if __name__ == "__main__":
    from src.logger import logging
    try:
        a = 1 / 0
    except Exception as e:
        logging.info("Divide by zero error test")
        raise CustomException(e, sys)
