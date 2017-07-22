"""
formatsql - lets you format SQL using the format_sql(, function.
"""

__version__ = '0.5'
__author__ = 'Ryan McGreal ryan@quandyfactory.com'
__copyright__ = 'Copyright 2009 by Ryan McGreal. Licenced under GPL version 2. http://www.gnu.org/licenses/gpl-2.0.html'


def replace_whitespace_with_space(char):
    """
    Takes a character and returns either the character (if it's not a whitespace character, or a single space
    """
    whitespace = '\t\n\x0b\x0c\r '
    if char in whitespace:
        return ' '
    else:
        return char


def convert_whitespace_to_space(instring):
    """
    Takes a string and converts any whitespace characters (spaces, tabs, returns, etc.) to spaces
    """
    return ''.join([replace_whitespace_with_space(s) for s in instring])


def remove_multiple_spaces(instring):
    """
    Takes a string and removes any multiple spaces
    """
    while '  ' in instring:
        instring = instring.replace('  ', ' ')
    return instring.strip()


def remove_multiple_blank_lines(instring):
    """
    Takes a string and removes multiple blank lines
    """
    while '\n\n' in instring:
        instring = instring.replace('\n\n', '\n')
    return instring.strip()


def prepare_inline_comments(instring):
    """
    Fixes inline comments starting with '--'
    """
    instring = instring.replace('--', '\n--')
    instring = instring.replace('-- ', '--')
    instring = instring.replace('--', '-- ')
    lines = instring.split('\n')
    outlist = []
    for line in lines:
        if line[:2] == '--':
            line += ' __TERMINATE__INLINE__COMMENT__'

        outlist.append(line)
    return ' '.join(outlist)


def set_linebreaks_and_tabs(instring):
    """
    Sets line breaks and tabs around SQL reserved words
    """
    # Step 1: initialize ignoreflag to False
    ignoreflag = False

    # Step 2: force multi-word SQL special syntax to behave like a single word
    instring = instring.replace('INNER JOIN', 'INNER&nbsp;JOIN')
    instring = instring.replace('LEFT JOIN', 'LEFT&nbsp;JOIN')
    instring = instring.replace('RIGHT JOIN', 'RIGHT&nbsp;JOIN')
    instring = instring.replace('GROUP BY', 'GROUP&nbsp;BY')
    instring = instring.replace('ORDER BY', 'ORDER&nbsp;BY')
    instring = instring.replace('DROP TABLE', 'DROP&nbsp;TABLE')
    instring = instring.replace('SET ANSI_NULLS ON', 'SET&nbsp;ANSI_NULLS&nbsp;ON')
    instring = instring.replace('SET QUOTED_IDENTIFIER ON', 'SET&nbsp;QUOTED_IDENTIFIER&nbsp;ON')
    instring = instring.replace(', ', '__COMMA__SPACE__')

    # Step 3: Split string into a list of words
    MyInWords = instring.split(' ')
    MyOutWords = []

    # Step 4: Hash table of keywords and their replacements
    tab_space_dict = {
        'ALTER': ' \n\nALTER\n',
        'PROCEDURE': '\nPROCEDURE\t',
        'FUNCTION': '\nFUNCTION\t',
        'EXEC': ' \n\nEXEC\t\t',
        'SELECT': '\n\nSELECT\t\t',
        'UPDATE': '\n\nUPDATE\t\t',
        'INSERT': '\n\nINSERT\t\t',
        'DELETE': '\n\nDELETE\t\t',
        'INTO': '\nINTO\t\t',
        'SET': '\nSET\t\t',
        'INNER&nbsp;JOIN': '\nINNER&nbsp;JOIN\t\t',
        'LEFT&nbsp;JOIN': '\nLEFT&nbsp;JOIN\t\t',
        'RIGHT&nbsp;JOIN': '\nRIGHT&nbsp;JOIN\t\t',
        'WHERE': '\nWHERE\t\t',
        'HAVING': '\nHAVING\t\t',
        'GROUP&nbsp;BY': '\nGROUP&nbsp;BY\t\t',
        'ORDER&nbsp;BY': '\nORDER&nbsp;BY\t\t',
        'FROM': '\nFROM\t\t',
        'ON': 'ON \n\t\t',
        'AND': '\n\t\tAND',
        'CASE': '\n\t\tCASE',
        'BEGIN': '\n\t\tBEGIN',
        'WHEN': '\n\t\t\tWHEN',
        'THEN': '\n\t\t\tTHEN',
        'ELSE': '\n\t\t\tELSE',
        'END': '\n\t\tEND',
        'DROP&nbsp;TABLE': '\n\nDROP&nbsp;TABLE\t\t',
        'SET&nbsp;ANSI_NULLS&nbsp;ON': '\nSET&nbsp;ANSI_NULLS&nbsp;ON',
        'SET&nbsp;QUOTED_IDENTIFIER&nbsp;ON': '\nSET&nbsp;QUOTED_IDENTIFIER&nbsp;ON',
        'GO ': '\nGO\n',
        '\tGO ': '\t\nGO\n',
        'VALUES': '\nVALUES\t\t',
        '(': '\n\t\t(\n\t\t',
        ')': '\n\t\t)\n\t\t',
    }

    # Step 5: Walk the list of words and do conversions for words not inside comments
    for word in MyInWords:
        if word == "/*" or word == '--':
            ignoreflag = True
        if word == '*/' or word == '__TERMINATE__INLINE__COMMENT__':
            ignoreflag = False

        if not ignoreflag:
            while word in tab_space_dict.keys():
                word = tab_space_dict[word]

            word = word.replace('__COMMA__SPACE__', ', \n\t\t')

        MyOutWords.append(word)

    outstring = ' '.join(MyOutWords)

    outstring = outstring.replace('__COMMA__SPACE__', ', ')
    outstring = outstring.replace('&nbsp;', ' ')

    # fix leading spaces after tabs
    while '\t ' in outstring:
        outstring = outstring.replace('\t ', '\t')

    return outstring


def convert_keywords_to_uppercase(instring):
    """
    Converts any SQL special keywords to uppercase
    """
    # convert string to list of individual words
    MyInWords = instring.split(' ')
    MyOutWords = []

    # list of SQL keywords to treat differently
    keywords = 'absolute action ada add all allocate alter and any are as asc assertion at authorization avg backup begin between bit bit_length both break browse bulk by cascade cascaded case cast catalog char char_length character character_length check checkpoint close clustered coalesce collate collation column commit compute connect connection constraint constraints contains containstable continue convert corresponding count create cross current current_date current_time current_timestamp current_user cursor database date day dbcc deallocate dec decimal declare default deferrable deferred delete deny desc describe descriptor diagnostics disconnect disk distinct distributed domain double drop dummy dump else end end-exec errlvl escape except exception exec execute exists exit external extract false fetch file fillfactor first float for foreign fortran found freetext freetexttable from full function get global go goto grant group having holdlock hour identity identity_insert identitycol if immediate in in include index index indicator initially inner inner input insensitive insert int integer intersect interval into into is isolation join key kill language last leading left level like lineno load local lower match max min minute module month names national natural nchar next no nocheck nonclustered none not null nullif numeric octet_length of off offsets on only open opendatasource openquery openrowset openxml option option or order outer output over overlaps pad partial pascal percent plan position precision prepare preserve primary print prior privileges proc procedure public raiserror read readtext real reconfigure references relative replication restore restrict return revoke right rollback rowcount rowguidcol rows rule save schema scroll second section select session session_user set setuser shutdown size smallint some space sql sqlca sqlcode sqlerror sqlstate sqlwarning statistics substring sum system_user system_user table temporary textsize then time timestamp timezone_hour timezone_minute to top trailing tran transaction translate translation trigger trim true truncate tsequal union unique unknown update updatetext upper usage use user using value values varchar varying view waitfor when whenever where while with work write writetext year zone'.split(
        ' ')

    # initialize ignoreflag = False
    ignoreflag = False

    # convert SQL keywords to uppercase
    for word in MyInWords:
        if word == "/*" or word == '--':
            ignoreflag = True
        if word == '*/' or word == '__TERMINATE__INLINE__COMMENT__':
            ignoreflag = False

        if not ignoreflag:
            if word in keywords:
                MyOutWords.append(word.upper())
            else:
                MyOutWords.append(word)
        else:
            MyOutWords.append(word)

    instring = ' ' + ' '.join(MyOutWords) + ' '
    return instring


def fix_block_comments(instring):
    """
    Moves bock comments into new lines (one line for comment opener, one line for comment text,
    one line for comment closer).
    """
    instring = instring.replace('/* ', '/*')
    instring = instring.replace('/*', '\n/*\n')
    instring = instring.replace('*/ ', '\n*/\n')
    return instring


def fix_tab_spaces_for_keywords(instring, spaces=8):
    """
    After the convert_tabs_to_spaces function converts tabs to spaces, this function checks the
    First word in each line and adds enough spaces to bump it up to the total number of spaces
    per tab (default is 8).
    """
    lines = instring.split('\n')
    outlist = []
    comment_flag = False
    for line in lines:
        if line[:2] == '/*' or line[:] == '--':
            comment_flag = True
        if line[:2] == '*/':
            comment_flag = False

        if not comment_flag:
            hit_space = False
            chars = 0
            for char in line:
                chars += 1
                if char == ' ':
                    hit_space = True
                    break
                if hit_space:
                    break
            if chars < spaces:
                diff = spaces - chars
                outlist.append(line[:chars] + ' ' * diff + line[chars:])
            else:
                outlist.append(line)
        else:
            outlist.append(line)

    outstring = '\n'.join(outlist)
    # fix ORDER BY and GROUP BY
    outstring = outstring.replace('ORDER   BY ', 'ORDER BY')
    outstring = outstring.replace('GROUP   BY ', 'GROUP BY')
    outstring = outstring.replace('INNER   JOIN   ', 'INNER JOIN')
    outstring = outstring.replace('DROP    TABLE   ', 'DROP TABLE')
    outstring = outstring.replace('LEFT    JOIN  ', 'LEFT JOIN')
    outstring = outstring.replace('RIGHT   JOIN   ', 'RIGHT JOIN')
    return outstring


def convert_tabs_to_spaces(instring, spaces=8):
    """
    Converts tab characters in a query into spaces. Default is 8 spaces per tab.
    """
    outstring = instring.replace('\t', ' ' * spaces)
    outstring = fix_tab_spaces_for_keywords(outstring)
    return outstring


def format_sql(instring):
    """
    Takes an unformatted string of SQL and returns a formatted string:
    * Removes multiple white space
    * Converts SQL keywords to UPPERCASE
    * Sets linebreaks and tabs for SQL statements
    """
    instring = ' ' + instring

    # fix inline comments
    instring = prepare_inline_comments(instring)

    # convert existing tabs and line breaks into spaces
    instring = convert_whitespace_to_space(instring)

    # eliminate multiple spaces
    instring = remove_multiple_spaces(instring)

    # convert keywords to uppercase
    instring = convert_keywords_to_uppercase(instring)

    # format SQL special charcters
    instring = set_linebreaks_and_tabs(instring)

    # NEW 2009-08-24 - format comments
    instring = fix_block_comments(instring)

    # fix inline comment terminator
    instring = instring.replace('__TERMINATE__INLINE__COMMENT__', '\n')

    # eliminate multiple spaces
    instring = remove_multiple_spaces(instring)

    # eliminate multiple blank lines
    instring = remove_multiple_blank_lines(instring)

    # converts tabs to spaces - default is 8
    instring = convert_tabs_to_spaces(instring)

    return instring.strip()



sql = """

SELECT mi.id, ifnull(mi.name, '') as name, mi.longitude, mi.latitude, mi.province, mi.city, mi.app_type as appType, mi.king_status as kingStatus, (if(mi.app_type = 'gxfw', if(mi.user_auth =1 OR mi.auth_status = 1, 1, (SELECT a.auth_status FROM merchant_auth a WHERE a.merchant_id = mi.id AND a.auth_status = 1 ORDER BY a.join_time DESC LIMIT 1)), (SELECT a.auth_status FROM merchant_auth a WHERE a.merchant_id = mi.id AND a.auth_status = 1 ORDER BY a.join_time DESC LIMIT 1))) auth_status, (SELECT GROUP_CONCAT(service_type_id) FROM merchant_service_type t WHERE t.merchant_id = mi.id) serviceTypeIds, (SELECT group_concat(t.service_type_name) FROM service_type t WHERE t.id IN (SELECT m.service_type_id FROM merchant_service_type m WHERE m.merchant_id = mi.id)) serviceTypeNames, ifnull( (SELECT u.nickname FROM user_info u WHERE u.id IN ((SELECT t.user_id FROM merchant_employees t WHERE t.is_del = 0 AND t.verification_status = 1 AND t.employees_type = 1 AND t.merchant_id = mi.id)) ORDER BY u.id LIMIT 1), '') nickname, ifnull((SELECT service_frequency FROM merchant_statistics t WHERE t.merchant_id = mi.id LIMIT 1), 0) AS serviceFrequency FROM merchant_info mi WHERE mi.is_del = 0 AND (mi.app_type = 'gxfw' OR (mi.NAME IS NOT NULL AND mi.NAME != "")) ORDER BY mi.id LIMIT 1120000, 10000
"""

formatted_sql = format_sql(sql)
print(formatted_sql)