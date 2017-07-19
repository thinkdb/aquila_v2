"""
给定一条SQL，列出SQL使用的表，表对应的字段信息，表中存在的索引，表的基本信息
"""
import re


class QueryTableParser(object):
    """
    获取任意一个sql语句中使用到 有效表名
    默认返回 返回一个空的元组集合
    """
    def __init__(self):
        self.pos = 0
        self.len = 0
        self.query = ""
        self.flag = 0
        self.table_tokens = [
            'from',
            'join',
            'update',
            'into'
        ]
        self.table_filter_tokens = [
            'WHERE',
            '(',
            ')'
        ]

    def parse(self, sql):
        """
        解析表名
        :param sql: 需要解析的 SQL 语句
        :return: 返回一个元组集合
        """
        # 替换 sql 文本中的任意空白字符为 空格, 并在逗号后面添加一个空格
        self.query = re.subn("\s+", " ", sql)[0]
        self.query = re.subn(",", ", ", self.query)[0]
        self.query = re.subn("\)", " ) ", self.query)[0]
        self.query = re.subn("\s+", " ", self.query)[0]
        self.query = re.subn("\s+\)", ")", self.query)[0]
        print(self.query)
        # 计算长度sql文本长度
        self.len = len(self.query)

        tables = []
        # 判断是否到了 SQL 文本末尾
        while self.has_next_token():
            # 获取两个空格之间的单词
            token = self.get_next_token()
            # 判断 token 是否在 table_tokens 中
            if self.table_tokens.count(token.lower()) or self.flag:
                # 如果在， 这边就开始获取表名

                # 这边处理别名问题
                if self.flag:
                    table_name = token
                else:
                    table_name = self.get_next_token()

                '''
                表名有个特性，字母开头，由下划线和数字组成， 这符合正则表达式中的 \w
                分隔出来的表名，可能是
                "table_name, table_name", "table_name", "table_name aa, table_name""
                "`table_name`, `table_name`", "`table_name`"
                '''
                # 匹配表名中有逗号
                if re.search(",", table_name):

                    # 表格式为 "table_name1, table_name2"
                    # 查找到 table_name1
                    while re.search(",", table_name):
                        if re.search('\w+', table_name.strip('`')):
                            table = re.sub('`', '', table_name.strip(','))
                            tables.append(table.strip(';'))
                        table_name = self.get_next_token()

                    # 查找到 table_name2
                    if re.search('\w+', table_name.strip('`')):
                        table = re.sub('`', '', table_name)
                        tables.append(table.strip(';'))
                # 匹配表名中没有逗号
                else:
                    # 判断表名是不是 where 和 ( 开头，是否继续下一个单词过滤
                    if self.table_filter_tokens.count(table_name.lower()) \
                            or table_name.startswith('('):
                        continue
                    if re.search('\w+', table_name.strip('`')):
                        table = re.sub('`', '', table_name)
                        tables.append(table.strip(';').strip(')'))

                    # 判断是否为别名
                    table_name = self.get_next_token()
                    if re.search(',', table_name):
                        self.flag = 1
                    else:
                        self.flag = 0

        return set(tables)

    def has_next_token(self):
        """
        判断是否已经全部检查完了
        :return: 返回 True or False
        """
        if self.pos >= self.len:
            return False
        return True

    def get_next_token(self):
        """
        获取按空格分隔后的每个单词，用于判断是否在self.table_tokens中
        :return: 返回两个空格之间的单词
        """
        # 从 sql 文本 self.pos 位置开始，搜索第一个空格
        # 比如 self.pos 为10， 那么是从 sql 文本中的第10个字符位置开始查找
        pos_flag = re.search("\s", self.query[self.pos:])

        # 没有搜索到，表示已经到sql文本末尾了
        if not pos_flag:
            pos = self.len
        else:
            # print(pos_flag)
            # --> <_sre.SRE_Match object; span=(5, 6), match=' '>
            # 这边表示搜索到的空格在原sql文本中的位置
            pos = pos_flag.span()[0] + self.pos
        start = self.pos
        end = pos
        self.pos = pos + 1
        return self.query[start:end]


class QueryRewrite(object):
    """
    转换 DML 语句为 select 语句, 针对insert, 只支持 insert into xx select xxx; 语句
    默认返回 None
    """
    def __init__(self):
        self.type = 0
        self.sql = None
        self.UNKNOWN = 11
        self.SELECT = 1
        self.DELETE = 2
        self.INSERT = 3
        self.UPDATE = 4
        self.ALTER = 5
        self.DROP = 6
        self.CREATE = 7
        self.DELETEMULTI = 8
        self.UNION = 9
        self.INSERTSELECT = 10
        self.TABLEREF = '`?[A-Za-z0-9_]+`?(\.`?[A-Za-z0-9_]+`?)?'

        self.COMMENTS_C = '/\s*\/\*.*?\*\/\s*/'
        self.COMMENTS_HASH = '/#.*$/'
        self.COMMENTS_SQL = '/--\s+.*$/'

    def format_sql(self, sql=None):
        self.sql = sql.upper()
        if not self.sql:
            return ''
        self.sql = re.subn(self.COMMENTS_C, '', self.sql)[0]
        self.sql = re.subn(self.COMMENTS_HASH, '', self.sql)[0]
        self.sql = re.subn(self.COMMENTS_SQL, '', self.sql)[0].strip()
        self.sql = re.subn("\s+", " ", self.sql)[0]
        self.figure_out_type()
        if self.type:
            return self.to_select()

    def figure_out_type(self):
        if re.search('^SELECT', self.sql):
            self.type = self.SELECT
        elif re.search('^DELETE\s+FROM\s', self.sql):
            self.type = self.DELETE
        elif re.search('^DELETE\s+'+self.TABLEREF+'\s+FORM\s', self.sql):
            self.type = self.DELETEMULTI
        elif re.search('^INSERT\s+INTO\s+.*[\s(]*SELECT\s+', self.sql):
            self.type = self.INSERTSELECT
        elif re.search('^INSERT\s+INTO\s', self.sql):
            self.type = self.INSERT
        elif re.search('^(.*)\s+UNION\s+(.*)$', self.sql):
            self.type = self.UNION
        elif re.search('^UPDATE\s', self.sql):
            self.type = self.UPDATE
        elif re.search('^ALTER\s', self.sql):
            self.type = self.ALTER
        elif re.search('^CREATE\s', self.sql):
            self.type = self.CREATE
        elif re.search('^DROP\s', self.sql):
            self.type = self.DROP
        else:
            self.type = self.UNKNOWN

    def to_select(self):
        select = None
        while not select:
            if self.type == self.SELECT:
                select = self.sql
                break
            elif self.type == self.UNION:
                select = self.sql
                break
            elif self.type == self.DELETE:
                select = re.subn('^DELETE\s+FROM\s', 'SELECT 0 FROM ', self.sql)[0]
                break
            elif self.type == self.DELETEMULTI:
                select = re.subn('^DELETE\s+'+self.TABLEREF+'\s+FORM\s', 'SELECT 0 FROM ', self.sql)[0]
                break
            elif self.type == self.UPDATE:
                if re.search('WHERE', self.sql):
                    subpatterns = re.match('^UPDATE\s+(.*)\s+SET\s+(.*)\s+WHERE\s+(.*)$', self.sql)
                    if subpatterns:
                        table_name, col_name, where_name = subpatterns.groups()
                        select = "SELECT {col_name} FROM {table_name} WHERE {where_name}".format(col_name=col_name,
                                                                                                 table_name=table_name,
                                                                                                 where_name=where_name)
                    break
                else:
                    subpatterns = re.match('^UPDATE\s+(.*)\s+SET\s+(.*)\s+(.*)$', self.sql)
                    if subpatterns:
                        table_name, col_name, where_name = subpatterns.groups()

                        select = "SELECT {colname}{where_name} FROM {table_name};".format(colname=col_name,
                                                                                          table_name=table_name,
                                                                                          where_name=where_name.strip(';'))
                    break
            elif self.type == self.INSERTSELECT:
                subpatterns = re.match('.*\)\s+(SELECT\s+.*)', self.sql)
                if subpatterns:
                    select = subpatterns.groups()[0].strip('"')
                    break
                else:
                    break
            else:
                break
        return select


sql_content = """
select * from (select * from (select * from  a ) b, c cc ) xxxx
"""

a = QueryRewrite()
b = a.format_sql(sql=sql_content)
print('sql 内容: ', b)

if b:
    a = QueryTableParser()
    tables = a.parse(b)
    print('使用的表名: ', tables or 0)

