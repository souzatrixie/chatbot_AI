import pandas as pd, mysql.connector
from math import sqrt

keysubstrings = {
              'item' : ('component', 'item', 'itens'),
          'function' : ('func', 'funç'),
       'requirement' : ('requi',),
              'mode' : ('mode', 'modo'),
            'effect' : ('effect', 'efeito', 'efecto'),
          'severity' : ('sever',),
    'classification' : ('clas',),
             'cause' : ('caus', 'mecha', 'meca'),
        'prevention' : ('preven',),
      'occurrence_p' : ('occur', 'ocor'),
         'detection' : ('detec', 'deteç'),
       'detection_p' : ('detec', 'deteç'),
    'recommendation' : ('recom', 'action', 'ação', 'ações'),
    'responsibility' : ('respons',),
       'target_date' : ('target', 'prazo'),
      'action_taken' : ('taken', 'tomada'),
    'effective_date' : ('effective', 'efetiv'),
          'action_s' : ('sever',),
          'action_o' : ('occur', 'ocor'),
          'action_d' : ('detec', 'deteç')
}

col_table = {
              'item' : 'components',
          'function' : 'functions',
       'requirement' : 'functions',
              'mode' : 'failures',
            'effect' : 'failures',
          'severity' : 'failures',
    'classification' : 'failures',
             'cause' : 'failures',
        'prevention' : 'failures',
      'occurrence_p' : 'failures',
         'detection' : 'failures',
       'detection_p' : 'failures',
    'recommendation' : 'actions',
      'action_taken' : 'actions',
    'responsibility' : 'actions',
       'target_date' : 'actions',
    'effective_date' : 'actions',
          'action_s' : 'actions',
          'action_o' : 'actions',
          'action_d' : 'actions'
}

def atoi(input:str) -> int:
    sign = 1
    num = 0
    try:
        c = input[0]
        if c == '-':
            sign = -1
        elif c.isdecimal():
            num += int(c)
        else:
            return 0
    except:
        return 0
    for c in input[1:]:
        if not c.isdigit():
            break
        num = num * 10 + int(c)
    return num * sign

# retorna a linha em que os dados provavelmente começam e um dicionário indicando a posição de cada coluna detectada
# ou retorna (None, None) caso não consiga localizar todas as colunas necessárias nas primeiras search_len linhas.
#
# file é o arquivo;
# sheet_index é o índice da planilha;
# search_len é a quantidade máxima de linhas a ser analizada antes de desistir.
def get_data_cols_from_doc(file:pd.ExcelFile, sheet_index:int, search_len:int = 30) -> tuple[int, dict] | tuple[None, None]:
    datalist = list(keysubstrings)
    data_cols = {}
    current_column = 0
    number_found = 0
    required_cols = len(keysubstrings)
    
    # nome do dado e as possíveis colunas e linhas em que ele pode estar
    candidates = {}
    for key in keysubstrings:
        candidates[key] = []
    
    contents = pd.read_excel(file, sheet_name=sheet_index, header=None, dtype=str, nrows=search_len, na_filter=False)
    
    # determina todas as possíveis colunas para cada dado do dfmea
    for row in contents.iterrows():
        current_column = 0
        for element in row[1]:
            element = element.casefold()
            if element.isnumeric() and len(candidates['item']) > 0:
                number_found = row[0]
                break
            for data in datalist:
                is_data_candidate = False
                for sub in keysubstrings[data]:
                    if sub in element:
                        is_data_candidate = True
                        break
                if is_data_candidate:
                    candidates[data].append([current_column, row[0]])
            current_column += 1
        if number_found:
            break
    
    # determina qual coluna é a mais provável para conter realmente o dado
    # leva em consideração a ordem dos dados e qual candidato ocorre antes
    current_column = -1
    start_row = -1
    if (len(candidates['item']) == 2 and candidates['item'][0][1] == candidates['item'][1][1] and 
            candidates['item'][1][0] - candidates['item'][0][0] == 3):
        candidates['item'][0][0] += 1
    table_cols = {'components':[], 'functions':[], 'failures':[], 'actions':[]}
    for key in candidates:
        if(not table_cols[col_table[key]]):
            table_cols[col_table[key]].append(current_column)
        data_row = -1
        for (col, row) in candidates[key]:
            # o current_column + 4 estabelece uma separação máxima entre duas colunas consecutivas
            # sem ele, o algoritmo pode consider uma coluna muito separada como fazendo parte de uma tabela
            if (min(table_cols[col_table[key]]) < col <= current_column + 4 and (col not in table_cols[col_table[key]]) and 
                    row != number_found and ((key not in data_cols) or col < data_cols[key])):
                data_cols[key] = col
                data_row = row
        if key in data_cols:
            table_cols[col_table[key]].append(data_cols[key])
            if current_column < data_cols[key]:
                current_column = data_cols[key]
            if data_row > start_row:
                start_row = data_row
    
    # até o momento, nalguns dfmeas:
    # `requirement` aparece junto com `function`;
    # `target_date` aparece junto com `responsibility`;
    # `effective_date` e `classification` não estão presentes.
    #  
    # Por esse motivo, o algoritmo precisa considerar a possibilidade de não detectá-los.
    # caso o algoritomo falhe em detectar alguma outra coluna, os dados do dfmea não serão extraídos.
    # 
    # Para `target_date`, talvez seja possível obte-la extraíndo os números de `responsibility`.
    for key in ('requirement', 'target_date', 'effective_date', 'classification'):
        if key not in data_cols:
            required_cols -= 1
    
    # Para depuração
    if 0:
        for key in candidates:
            print(f'\t{key} - {candidates[key]}\n\t{data_cols[key] if key in data_cols else ''}')
    if 0:
        print(f"d {len(data_cols) - required_cols} s {start_row}\nn {number_found}")
    
    if len(data_cols) != required_cols:
        return None, None
    return start_row + 1, data_cols

# retorna uma lista contendo:
# -- o id do projeto, do banco de dados;
# -- o número do projeto, caso encontre;
# -- o nome do projeto, caso encontre.
# caso não esteja no banco, o id será None.
# 
# é importante destacar que ele busca baseado no número do projeto ou no nome do arquivo, o nome do projeto
# não é utilizado devido a dificuldade em localizá-lo. O número do projeto possui precedência sobre o nome do arquivo.
# 
# file é o arquivo e filename é o nome do arquivo a partir do diretório contendo os dfmeas, definido previamente
# é importante informar o filename a partir do diretório pois o banco usa um VARCHAR(255) para ele
def get_project_info_from_db(file:pd.ExcelFile, filename:str, connection:mysql.connector.MySQLConnection, search_len:int = 30) -> tuple[int | None, str | None, str | None]:
    contents = pd.read_excel(file, header=None, dtype=str, na_filter=False, nrows=search_len)
    number_labels = []
    name_labels = []
    number_cells = []
    for row in contents.iterrows():
        filtered_cols = row[1].loc[row[1].str.contains('project|projeto', case=False)]
        if(len(filtered_cols)):
            for cell in filtered_cols.loc[filtered_cols.str.contains('number|número|nº|num', case=False)].items():
                number_labels.append(pd.Series([row[0], cell[0]], ['row', 'col']))
            for cell in filtered_cols.loc[filtered_cols.str.contains('nome|name', case=False)].items():
                name_labels.append(pd.Series([row[0], cell[0]], ['row', 'col']))
        for cell in row[1].loc[row[1].str.contains('PRJ', case=False)].items():
            number_cells.append(pd.Series([row[0], cell[0]], ['row', 'col']))
    
    project_number = None
    project_name = None
    if len(number_cells) == 1:
        pos = contents.iat[*number_cells[0].values].upper().find("PRJ")
        project_number = contents.iat[*number_cells[0].values][pos:pos + 16].rstrip()
    elif len(number_labels) == 1:
        min_dist_ind = None
        min_dist = None
        for ind in range(len(number_cells)):
            if number_cells[ind].iat[1] >= number_labels[0].iat[1]:
                diff = (number_cells[ind] - number_labels[0])
                distance = sqrt(diff['row'] ** 2 + diff['col'] ** 2)
                if min_dist == None or min_dist > distance:
                    min_dist = distance
                    min_dist_ind = ind
        if min_dist != None:
            number_cells = [number_cells[min_dist_ind]]
            pos = contents.iat[*number_cells[0].values].upper().find("PRJ")
            project_number = contents.iat[*number_cells[0].values][pos:pos + 16].rstrip()
    
    if len(name_labels) == 1 and len(number_labels) == 1 and len(number_cells) == 1:
        name_labels[0] += number_cells[0] - number_labels[0]
        project_name = contents.iat[*name_labels[0].values]
        pos = project_name.find(':')
        project_name = project_name[(pos if pos >= 0 else 0):].lstrip()
        if project_name == '':
            project_name = None
    
    filename = filename[0:filename.rfind('.')]
    
    # busca pelo projeto
    cursor = connection.cursor()
    if project_number != None:
        cursor.execute('SELECT `id` FROM dfmeas WHERE `project_number` = %s', (project_number,))
        id = cursor.fetchone()
        cursor.fetchall()
        if id:
            return id[0], project_number, project_name
    cursor.execute('SELECT `id` FROM dfmeas WHERE `filename` = %s', (filename,))
    id = cursor.fetchone()
    cursor.fetchall()
    if id:
        return id[0], project_number, project_name
    return None, project_number, project_name

# caso o projeto não esteja no banco (indicado por project_id == None), insere os dados dele (nome do projeto,
# número do projeto e o nome do arquivo, sem a extensão) na tabela `dfmeas`;
# caso esteja, atualiza essas informações na tabela `dfmeas`, útil caso o número ou nome sejam incluidos ou caso haja
# uma mudança no nome do arquivo, e deleta os dados referentes a esse projeto das tabelas selecionadas, para que eles
# possam ser inseridos posteriormente. Essa é a única forma de garantir que os dados serão atualizados sem repetição.
# 
# em ambos casos, retorna o id do projeto.
# 
# project_id é o id do projeto, obtido por get_project_info_from_db;
# project_number é o número do projeto, obtido por get_project_info_from_db; 
# project_name é o nome do projeto, obtido por get_project_info_from_db;
# filename é o nome do arquivo com a extensão;
# overwrite_mode indica a partir de qual tabela os valores serão atualizados (deletados). No geral, é melhor usar 'full'.
def insert_project_into_db(project_id:int|None, project_number:str, project_name:str, filename:str, overwrite_mode:str, connection:mysql.connector.MySQLConnection) -> int:
    cursor = connection.cursor()
    filename = filename[0:filename.rfind('.')]
    
    if project_id == None:
        cursor.execute('''INSERT INTO `dfmeas` (`project_name`, `project_number`, `filename`) VALUES (%s, %s, %s)''', 
                (project_name, project_number, filename))
        connection.commit()
        cursor.execute('SELECT `id` FROM dfmeas WHERE `filename` = %s', (filename,))
        project_id = cursor.fetchone()
        cursor.fetchall()
        return project_id
    
    # caso o projeto já esteja no banco
    # esse encadeamento é feio, mas é mais otimizado que que a forma antiga
    # se tivesse switch-case com fallthrough...
    if overwrite_mode in ('full', 'components','functions', 'failures', 'actions', 1, 2, 3, 4):
        cursor.execute('''DELETE FROM `actions` USING `actions`
                       LEFT JOIN `failures` ON `actions`.failure_id = `failures`.id
                       LEFT JOIN `functions` ON `failures`.function_id = `functions`.id
                       LEFT JOIN `components` ON `functions`.component_id = `components`.id
                       WHERE `components`.project_id = %s''', (project_id,))
        connection.commit()
        
        if overwrite_mode in ('full', 'components','functions', 'failures', 2, 3, 4):
            cursor.execute('''DELETE FROM `failures` USING `failures`
                        LEFT JOIN `functions` ON `failures`.function_id = `functions`.id
                        LEFT JOIN `components` ON `functions`.component_id = `components`.id
                        WHERE `components`.project_id = %s''', (project_id,))
            connection.commit()
            
            if overwrite_mode in ('full', 'components', 'functions', 3, 4):
                cursor.execute('''DELETE FROM `functions` USING `functions`
                            LEFT JOIN `components` ON `functions`.component_id = `components`.id
                            WHERE `components`.project_id = %s''', (project_id,))
                connection.commit()
                
                if overwrite_mode in ('full', 'components', 4):
                    cursor.execute('''DELETE FROM `components`
                                WHERE `components`.project_id = %s''', (project_id,))
                    connection.commit()
    
    cursor.execute('''UPDATE `dfmeas` SET `project_name` = %s, `project_number` = %s, `filename` = %s WHERE `id` = %s''',
            (project_name, project_number, filename, project_id))
    connection.commit()
    return project_id

# insere os dados dos dfmeas no banco
# 
# columns é um dicionário contendo os dados localizados e a coluna em que estão
def insert_sheet_datas_into_db(file:pd.ExcelFile, project_id:int, sheet_index:int, connection:mysql.connector.MySQLConnection, initial_row:int, columns:dict):
    old_data = {}
    new = {'components':False, 'functions':False, 'failures':False, 'actions':False}
    id = {'components':0, 'functions':0, 'failures':0, 'actions':0}
    cascade_columns = ['item', 'function', 'requirement', 'mode', 'effect', 'cause', 'prevention', 'detection']
    action_columns = ['recommendation', 'action_taken', 'responsibility', 'target_date', 'effective_date']
    null_values = ('', 'none', 'nan', 'na', 'nada')
    
    # *_queries[...][1] contém o comando SQL para inserir e selecionar o que é importante
    # *_queries[...][0] contém os dados que serão utilizados nas queries, con exceção do id
    select_queries = {
        'components' : (['item'],
                        '''SELECT `id` FROM `components` WHERE `project_id` = %s AND `name` = %s;'''
                        ),
        'functions' : (['function'],
                        '''SELECT `id` FROM `functions` WHERE `component_id` = %s AND `function` = %s;'''
                        ),
        'failures' : (['mode', 'effect', 'cause', 'prevention', 'detection'],
                        '''SELECT `id` FROM `failures` WHERE `function_id` = %s AND `mode` = %s AND `effect` = %s
                        AND `cause` = %s AND `prevention_control` = %s AND `detection_control` = %s;'''
                        ),
        'actions' : (['recommendation'],
                        '''SELECT `id` FROM actions WHERE `failure_id` = %s AND `recommended` = %s;'''
                        )
    }
    insert_queries = {
        'components' : (['item'],
                        '''INSERT INTO `components` (`project_id`, `name`) VALUES (%s, %s);'''
                        ),
        'functions' : (['function', 'requirement'],
                        '''INSERT INTO `functions` (`component_id`, `function`, `requirements`) VALUES (%s, %s, %s);'''
                        ),
        'failures' : (['mode', 'effect', 'classification', 'cause', 'prevention', 'detection', 'severity', 'occurrence_p', 'detection_p'],
                        '''INSERT INTO `failures` (`function_id`, `mode`, `effect`, `classification`, `cause`, `prevention_control`,
                        `detection_control`, `severity`, `occurrence`, `detection`)  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
                        ),
        'actions' : (['recommendation', 'action_taken', 'responsibility', 'target_date', 'effective_date', 'action_s', 'action_o', 'action_d'],
                        '''INSERT INTO `actions` (`failure_id`, `recommended`, `taken`, `responsibility`, `target_date`, `effective_date`,
                        `severity`, `occurrence`, `detection`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'''
                        )
    }
    
    # esse é apenas para informar quantos dados foram adicionados
    total = [0, 0, 0, dict({'components':0, 'functions':0, 'failures':0, 'actions':0})]
    
    contents = pd.read_excel(file, sheet_name=sheet_index, header=None, dtype=str,
            skiprows=initial_row, na_filter=False, usecols=list(columns.values()))
    contents.rename(columns=dict(zip(columns.values(), columns.keys())), inplace=True)
    contents = contents.map(lambda x : x.rstrip().lstrip())
    # esse serve para substituir todas as novas linhas por espaço
    #contents = contents.map(lambda x : x.replace('\r\n', '\n')).map(lambda x : x.replace('\r', '\n')).map(lambda x : x.replace('\n', ' '))
    contents = contents.map(lambda x : None if (x.casefold() in null_values) else x)
    
    # os dados problemáticos
    if 'requirement' not in columns:
        contents.insert(loc=0, column='requirement', value=None)
        cascade_columns.remove('requirement')
    if 'target_date' not in columns:
        contents.insert(loc=0, column='target_date', value=None)
        action_columns.remove('target_date')
    if 'effective_date' not in columns:
        contents.insert(loc=0, column='effective_date', value=None)
        action_columns.remove('effective_date')
    if 'classification' not in columns:
        contents.insert(loc=0, column='classification', value=None)
    
    cursor = connection.cursor()
    
    for row in contents.iterrows():
        total[0] += 1
        new_data = row[1]

        new_data['severity'] = atoi(new_data['severity'])
        new_data['occurrence_p'] = atoi(new_data['occurrence_p'])
        new_data['detection_p'] = atoi(new_data['detection_p'])
        
        # checagem dos valores necessários
        sod = False
        if (new_data['severity'] and new_data['detection_p'] and new_data['occurrence_p']):
            sod = True
            total[1] += 1
        
        # ajuste dos valores SOD das ações tomadas, muitas tabelas não colocam todos os valores
        new_data['action_s'] = atoi(new_data['action_s'])
        new_data['action_o'] = atoi(new_data['action_o'])
        new_data['action_d'] = atoi(new_data['action_d'])
        
        if not new_data['action_s']:
            new_data['action_s'] = new_data['severity']
        if not new_data['action_o']:
            new_data['action_o'] = new_data['occurrence_p']
        if not new_data['action_d']:
            new_data['action_d'] = new_data['detection_p']
        
        # determina se há um novo dado nas tabelas com colunas cascata (as que ramificam)
        # nota-se que new['components'] implica new['functions'], que implica new['failures']
        valid = False
        for key in cascade_columns:
            if new_data[key] and (key not in old_data or valid or new_data[key] != old_data[key]):
                new[col_table[key]] = True
                valid = True
                old_data[key] = new_data[key]
            elif key == 'requirement':
                old_data[key] = new_data[key]
            elif valid:
                valid = False
                break
            else:
                new[col_table[key]] = False
                try:
                    new_data[key] = old_data[key]
                except KeyError:
                    valid = False
                    break
        if new['actions']:
            new['failures'] = True
        if new['failures']:
            new['functions'] = True
        if new['functions']:
            new['components'] = True
        
        if not (valid and sod):
            continue
        total[2] += 1
        
        # determina se há um novo dado para a tabela actions
        # separada pois new['failures'] não implica new['actions']
        if new_data['recommendation']:
            new['actions'] = True
        else:
            new['actions'] = False
        
        prev_table = None
        for table in ('components', 'functions', 'failures', 'actions'):
            if new[table]:
                if prev_table:
                    select_values = [id[prev_table]]
                else:
                    select_values = [project_id]
                for key in select_queries[table][0]:
                    select_values.append(new_data[key])
                cursor.execute(select_queries[table][1], tuple(select_values))
                result = cursor.fetchone()
                cursor.fetchall()
                if result:
                    id[table] = result[0]
                else:
                    if prev_table:
                        insert_values = [id[prev_table]]
                    else:
                        insert_values = [project_id]
                    for key in insert_queries[table][0]:
                        insert_values.append(new_data[key])
                    cursor.execute(insert_queries[table][1], tuple(insert_values))
                    connection.commit()
                    cursor.execute(select_queries[table][1], tuple(select_values))
                    id[table] = cursor.fetchone()[0]
                    cursor.fetchall()
                    total[3][table] += 1
            prev_table = table
    
    # imprime os resultados, para depuração
    if 0:
        print(f'{total[0]} lidas\n{total[1]} com SOD\n{total[2]} válidas')
        print(f'{total[3]['components']} adicionadas em `components`')
        print(f'{total[3]['functions']} adicionadas em `functions`')
        print(f'{total[3]['failures']} adicionadas em `failures`')
        print(f'{total[3]['actions']} adicionadas em `actions`\n')

# essa função unifica todas as outras
# é particamente a única que precisa ser importada, mas seria bom mudar algumas coisas nela, talvez para interagir com o usuário
# e corrigir o número ou o nome do projeto, caso esteja errado, ou informá-lo se o projeto já está no banco e perguntar-lhe se ele
# quer atualizar as informações 
def insert_dfmeas_into_db(dfmea_directory:str, filename:str, connection:mysql.connector.MySQLConnection, search_len:int = 30, overwrite_mode:str = None):
    file = pd.ExcelFile(dfmea_directory + filename, engine='calamine')
    sheet = 0
    
    # depuração
    if 0:
        print(f"{filename}")
    
    start_row, columns = get_data_cols_from_doc(file, sheet, search_len)
    if start_row != None:
        id, number, name = get_project_info_from_db(file, filename, connection, start_row - 1)
        if overwrite_mode != None or id == None:
            id = insert_project_into_db(id, number, name, filename, overwrite_mode, connection)
            while(start_row != None):
                
                if 0:
                    print(f'sheet {sheet}')
                
                insert_sheet_datas_into_db(file, id, sheet, connection, start_row, columns)
                sheet += 1
                start_row, columns = get_data_cols_from_doc(file, sheet, search_len)