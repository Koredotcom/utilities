ORDER_INFORMATION = 'Order Information'
FIRST_TOC_PREFIX = 'English'
TABLE_MARK_DOWN_PREFIX = '![table]('
MARK_DOWN_SUFFIX = ')'
TABLE = 'table'
CLI_FLAG_PATTERN = r'(?P<pack_size>\d{1,4})\s*tests'


# template types
AMENDMENT_TEMPLATE = 'Ammendment Template'
VAL_TEMPLATE = 'ValueSheet Template'
INVAL_TEMPLATE = 'InValueSheet Template'
INVALID_TEMPLATE = 'Invalid Template'

# IC analyzer templates
BETWEEN_TABLE_ANALYZER = 'BetweenTableAnalyzer'
IN_TABLE_ANALYZER = 'InTableAnalyzer'
FIRST_PAGE_ANALYZER = 'FirstPageAnalyzer'

# CC analyzer templates
STANDARD_LAYOUT = 'Standard Layout'

# Value_extractor_util
SEARCH_RANGE_FOR_TEST_NAME = 11

LEVEL_LOOKUP = {
    'positive': 'Positive',
    'negative': 'Negative',
    'level i': '1',
    'level ii': '2',
    'level iii': '3',
}

CC_VS_ROW_DELTA = {"x0": -110, "y0": 0, "x1": 50, "y1": 0}

# operator manual constants
OM_COMPLETE_PAGE_DELTA = {'x0': 47, 'y0': 50, 'x1': -46, 'y1': -35}
OM_PARTIAL_PAGE_DELTA = {'x0': 47, 'y0': 50, 'x1': -46, 'y1': 0}
OM_ANSWER_PAGE_COUNT = 30
OM_PARENT_APPENDER = ' '
