import re

# SQL Grammar reference: https://forcedotcom.github.io/phoenix/

COMMAND_LIST = ["SELECT", "FROM", "WHERE", "LIMIT"]


class Query:
    def __init__(self, select, sub_select=None):
        self.select = select
        self.sub_select = sub_select


class Select:
    def __init__(self, columns, table_name, conditions=None, limit=None):
        self.columns = columns
        self.table_name = table_name
        self.conditions = conditions
        self.limit = limit

class Condition:
    def __init__(self, condition, prefix_op=None):
        self.operation = condition
        self.prefix_op = prefix_op

def get_query_list(statement):
    query_list = statement.split(";")
    # empty string
    if len(query_list) == 1 and query_list[0] == '':
        return None

    if len(query_list) > 1 and query_list[-1] == '':
        query_list = query_list[0:-1]

    return map(str.strip, query_list)


def process_select_statement(select_statement):
    select_tokens = re.split(COMMAND_LIST[0], select_statement, flags=re.IGNORECASE)
    assert select_tokens[0] is '', "Syntax error: a query must start with SELECT."
    assert len(select_tokens) == 2, "Syntax error: invalid SELECT statement."

    from_tokens = re.split(COMMAND_LIST[1], select_tokens[1], flags=re.IGNORECASE)
    assert len(from_tokens) == 2, "Syntax error: invalid select statement at FROM command."

    columns_str = from_tokens[0]
    columns = []
    for c in columns_str.split(","):
        columns.append(c.strip())

    where_tokens = re.split(COMMAND_LIST[2], from_tokens[1], flags=re.IGNORECASE)

    table_name = where_tokens[0].strip()
    assert len(table_name) > 0, "Syntax error: Table name cannot be empty."

    conditions = []
    operators = [None] # No prefix op if only one condition exists
    limit = None
    limit_token = []
    if len(where_tokens) > 1:
        print where_tokens
        limit_token = re.split(where_tokens[1], COMMAND_LIST[3], flags=re.IGNORECASE)
        where_conditions_str = limit_token[0]
        l = 0
        for w in re.split('(AND|,|OR) ', where_conditions_str, flags=re.IGNORECASE):
            if l % 2 == 0:
                conditions.append(process_where_expression(w.strip()))
            else:
                operators.append(w.strip().upper())
            l += 1
    else:
        conditions = None
        limit_token = re.split(from_tokens[1], COMMAND_LIST[3], flags=re.IGNORECASE)

    print limit_token
    if type(limit_token) is list and len(limit_token) > 0: limit = limit_token[1]

    return columns, table_name, conditions, operators, limit


def process_where_expression(exp):
    tokens = re.split("(IN|LIKE|BETWEEN|IS|=|<>|<=|>=|!=)", exp, flags=re.IGNORECASE)
    assert len(tokens) == 3, "Syntax error in where expression: " + str(exp)
    conditions = []
    for t in tokens:
        conditions.append(t.strip())
    return conditions


def parse(sql_statement):
    query_string_list = get_query_list(sql_statement)
    query_list = []
    for qs in query_string_list:
        columns, table_name, conditions, operators, limit = process_select_statement(qs)
        conditions_list = []
        op = 0
        for c in conditions:
            conditions_list.append(Condition(c,operators[op]))
            op += 1
        select = Select(columns, table_name, conditions_list, limit)
        query = Query(select)
        query_list.append(query)

    return query_list




