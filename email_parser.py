import json
from datetime import datetime
import chardet
from bs4 import BeautifulSoup
import re

# Функция для загрузки данных JSON из файла
def load_json_from_file(filename):
    with open(filename, 'r', encoding='UTF-8') as file:
        data = json.load(file)
    return data

# Функция для извлечения текста из HTML
def extract_text_from_html(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.get_text(separator="\n").strip()

# Функция для удаления email-адресов из текста
def remove_emails(text):
    ''' очистки текста от email'''
    return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '', text)

# Функция для удаления строк, начинающихся с определённых слов
def clean_plain_text_body(text_body):
    ''' функция очистки текста '''
    # удаляем почту из сообщения
    text_body = remove_emails(text_body)
    # разбиваем на строки
    lines = text_body.splitlines()
    # Список шаблонов для удаления строк
    
    '''паттерн для удаления строк начинающихся с этих символов'''
    patterns_to_remove = [
        # r'From',
        r'Sent',
        r'To',
        r'Subject',
        r'Date',
        r'date',
        r'<',
        r'>',
        r'$$',
        r'С уважением',
        r'Mrs',
        r'Тел',
        r'Tel',
        r'Моб',
        r'Mob',
        r'Whats',
        r'Сот:',
        r'Сот.',
        r'сот:',
        r'сот.',        
        r'e-mail',
        r'E-mail',
        r'Email',
        r'www',
        r'http',
        r'https',
        r'<http',
        r'<https',
        r'Описание:',
        r'Cc:',
        r'--',
        r'==',
        # r'\*\*',
        r'№',
        # r'\+',
        r'\[',
        r'C:',
        r'D:',
        r'E:',
        r'F:',
        r'АО',
        # r'Центр',
        r'Отправлено',
        r'oтправлено',
        r'Республика',
        r'Загр',
        r'пасп',
        r'с уважением',
        # r'От:',
        # r'От кого',
        r'Кому:',
        r'Have',
        r'Best',
        r'Благодар',
        r'понедельник',
        r'вторник',
        r'среда',
        r'четверг',
        r'пятница',
        r'суббота',
        r'воскресенье',
        r'Raspisanie',
        r'Тел',
        r'Факс',
        r'Эл.',
        r'Importance',
        r'Без вирусов',
        r'Logo',
        r'с/у',
        r'Вт,',
        r'Caution',
        r'VISA'
    ]

    # Создаем регулярное выражение из списка шаблонов
    pattern = '|'.join(patterns_to_remove)
    # Удаляем строки, которые соответствуют шаблонам
    cleaned_lines = [line.strip() for line in lines if not re.match(pattern, line.strip(), re.IGNORECASE)]

    '''паттерн на замену'''
    patterns_to_rename = [
        r'From:',
        # r'Здравствуйте,уважаемый пассажир!'
    ]   
    # Создаем регулярное выражение из списка шаблонов
    pattern = '|'.join(patterns_to_rename)

    # cleaned_lines = [re.sub(pattern, "Вопрос клиента:", line, flags=re.IGNORECASE).lstrip() for line in cleaned_lines]

    # Обработка строк: если строка начинается на "From", заменить её на "Вопрос клиента"
    cleaned_lines = ["\nВопрос клиента:" if re.match(pattern, line, flags=re.IGNORECASE) else line.strip() for line in cleaned_lines]
    
    # # удалем все номера телефонов  паспортные данные 
    patterns_to_remove = [
    r'\+?\d{1,2} ?$$\d{3}$$ ?$$\d{3}$$ ?$$\d{2}$$ ?$$\d{2}$$',  # соответствует всем вариантам написания сотового телефона
    r'\+?\d{1,2} ?\d{3} ?\d{3} ?\d{2} ?\d{2}',                  # соответствует всем вариантам написания сотового телефона
    r'\d[- ]?\d{3}[- ]?\d{3}[- ]?\d{4}',                        # соответствует вариантам написания телефонного номера 8-777-781-8194 или 8 777 781 8194
    r'$$\d{4}$$ ?\d{3} ?\d{3}',                                 # соответствует вариантам написания телефонного номера (7172) 777 789
    r'\d{3} ?\d{3} ?\d{4}',                                     # соответствует вариантам написания телефонного номера 777 227 6021
    r'\d ?\d{3} ?\d{3} ?\d{2}',                                 # соответствует вариантам написания телефонного номера 7 777 514 55
    r'\d{3}-?\d{3}-?\d{2}-?\d{2}',                              # соответствует вариантам написания телефонного номера 777-993-21-12
    r'\d{3} ?\d{2} ?\d{3} ?\d{2}',                              # соответствует вариантам написания телефонного номера 707 13 777 90
    r'$$\d{3}$$ ?\d{3}-?\d{2}-?\d{2}',                          # соответствует вариантам написания телефонного номера (777) 520-75-40
    r'-?\d{3}-?\d{3}-?\d{2}-?\d{2}',                            # соответствует вариантам написания телефонного номера -777-244-57-71
    r'\d{3} ?\d{3} ?\d{4}',                                     # соответствует вариантам написания телефонного номера 777 444 2227
    r'$$\d{3,4}$$ ?\d{3}-?\d{2}-?\d{2}',                        # соответствует вариантам написания телефонного номера (777) 520-75-40
    r'$$\d{4}$$ ?\d{3} ?\d{3}',                                 # соответствует вариантам написания телефонного номера (7172) 777 789
    r'\d{5,}',                                                  # соответствует числам с более чем 4 знаками
    ]
    # Создаем регулярное выражение из списка шаблонов
    pattern = '|'.join(patterns_to_remove)
    # Удаляем строки, которые соответствуют шаблонам
    full_cleaned_lines = [line.strip() for line in cleaned_lines if not re.search(pattern, line.strip())]

    cleaned_text = "\n".join(full_cleaned_lines).strip()

    # Замена множественных переносов строк на один
    # cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
    return cleaned_text

# Функция для разбора данных электронной почты
def parse_emails(email_list):
    parsed_data = []
    for email in email_list:
        plain_text_body = email.get("plain_text_body", "")

        if plain_text_body and "No Body" not in plain_text_body:
            plain_text_body = clean_plain_text_body(plain_text_body.strip())
        
            email_data = {
                "plain_text_body": plain_text_body,
            }
  
            parsed_data.append(email_data)
    
    return parsed_data

def save_to_file(parsed_emails, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for i, email in enumerate(parsed_emails):
            file.write(f"## Текст письма №{i}:\nОтвет службы поддержки:\n{email['plain_text_body']}\n\n")

# Основная функция
def main(filename:str, output_filename:str):
    # Загрузка данных JSON из файла
    
    try:
        emails = load_json_from_file(filename)
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        return
    except UnicodeDecodeError as e:
        print(f"Ошибка декодирования файла: {e}")
        return
    
    # Разбор данных электронной почты
    try:
        parsed_emails = parse_emails(emails)
    except TypeError as e:
        print(f"Ошибка разбора электронной почты: {e}")
        return
  
    # Сохранение данных в файл
    save_to_file(parsed_emails, output_filename)
    print(f"Данные успешно сохранены в файл: {output_filename}")

# Запуск основной функции
if __name__ == "__main__":
    base_dir = 'base/'

    filename = base_dir + 'input/emails.json'
    output_filename = base_dir + 'output/emails.txt'

    main(filename, output_filename)
