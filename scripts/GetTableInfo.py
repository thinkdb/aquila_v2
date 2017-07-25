

def get_table_info(dbapi, table_list):
    table_info_dict = {}
    for table in table_list:
        table_status_sql = "show table status like '{table_name}'".format(table_name=table.lower())
        index_status_sql = "show index from {table_name}".format(table_name=table.lower())
        table_structure_sql = "show create table {table_name}".format(table_name=table.lower())

        table_status_result = dbapi.conn_query(table_status_sql)
        table_col_info = dbapi.get_col()

        index_status_result = dbapi.conn_query(index_status_sql)
        index_col_info = dbapi.get_col()

        table_structure_result = dbapi.conn_query(table_structure_sql)
        str_col_info = dbapi.get_col()
        # for line in table_structure_result:
        #     for item in line[1]:
        #         pass

        table_info = {
            'table_info': {
                'status': table_status_result,
                'col': table_col_info
            },
            'index_info': {
                'status': index_status_result,
                'col': index_col_info
            },
            'structure': {
                'status': table_structure_result,
                'col': str_col_info
            }
        }
        table_info_dict[table] = table_info
    return table_info_dict
