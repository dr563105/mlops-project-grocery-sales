import prep

def lambda_handler(event, context=None) -> dict:
    """
    lambda handler for predict method
    """
    return prep.init(event)
