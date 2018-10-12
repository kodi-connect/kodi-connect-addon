import re

def string_to_ascii(string):
    # switch to ascii
    string = string.encode('ascii','ignore')
    # remove special chars , switch to lower, trim leading and trailing spaces
    string = re.sub(r'[?|$|!|:|#|\.|\,|\']',r'',string).lower()
    # remove multiple spaces
    string = re.sub(' +',' ',string)
    logger.debug('String after cleanup: {}'.format(string))
    return string
