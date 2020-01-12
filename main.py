import requests
import os
from datetime import datetime


def create_file(item, file_path, tmpl):
    '''
        Создает файл, и возвращает статус: True если файл создался, иначе False
    '''
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(tmpl.format(
                name=item['info'][1],
                email=item['info'][2],
                created= datetime.now().strftime('%d.%m.%Y %H:%M'),
                company_name=item['info'][3],
                completed='\n'.join(item['completed']) if item['completed'] else 'Пусто',
                not_completed='\n'.join(item['not_completed']) if item['not_completed'] else 'Пусто',
            ))
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    try:
        r_users = requests.get('https://jsonplaceholder.typicode.com/users')
        r_todos = requests.get('https://jsonplaceholder.typicode.com/todos')
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        users = {}

        # В словарь users записывается информация о человеке. {id: {info: (username, name, email, company_name)}}
        for item in r_users.json():
            users[item['id']] = {'info': (item['username'], item['name'], item['email'], item['company']['name'])}

        # В словарь users записываются задачи человека. {id: {..., completed: [...], not_completed: [...] }}
        for item in r_todos.json():
            if users.get(item['userId']):
                title = item['title'] if len(item['title']) < 50 else item['title'][:50] + '...'
                status = 'completed' if item['completed'] else 'not_completed'
                users[item['userId']].setdefault(status, []).append(title)

        # Создётся папка tasks если её не существует
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks')
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Шаблон для записи в файл
        tmpl = '{name} <{email}> {created}\n{company_name}\n\nЗавершённые задачи:\n{completed}\n\nОставшиеся задачи:\n{not_completed}'

        # Создаются файлы из полученной информации
        for item in users.values():
            file_path = os.path.join(directory, item['info'][0] + '.txt')

            if not os.path.exists(file_path):
                create_file(item, file_path, tmpl)
            else:
                updated_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%dT%H-%M')
                new_file_path = os.path.join(directory, item['info'][0] + '_' + updated_date + '.txt')
                os.rename(file_path, new_file_path)

                if not create_file(item, file_path, tmpl):
                    os.rename(new_file_path, file_path)
                