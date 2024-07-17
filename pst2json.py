# -*- coding: utf-8 -*-

import pypff
import json
import os

def extract_message_data(message):
    data = {
        "subject": message.subject if message.subject else "No Subject",
        "sender_name": message.sender_name if message.sender_name else "Unknown Sender",
        "sent_on": message.delivery_time.isoformat() if message.delivery_time else "No Date",
        "plain_text_body": message.plain_text_body.decode('utf-8', errors='ignore') if message.plain_text_body else "No Body",
        # "recipients": []
    }
    # for recipient in message.recipients:
    #     data["recipients"].append({
    #         "name": recipient.name if recipient.name else "Unknown",
    #         "address": recipient.address if recipient.address else "No Address"
    #     })

    # print(message.plain_text_body.decode('utf-8', errors='ignore'))
    return data

def process_folder(folder, path=""):
    messages = []
    try:
        folder_name = folder.name if folder.name else "Unnamed Folder"
        print('извлекаем письма из папки:', folder_name)
        current_path = os.path.join(path, folder_name)
        for item in folder.sub_messages:
            messages.append(extract_message_data(item))

        for sub_folder in folder.sub_folders:
            messages.extend(process_folder(sub_folder, current_path))
    except Exception as e:
        print(f"Error processing folder '{current_path}': {e}")

    return messages



def find_sent_folder(folder):
    try:
        if folder.name == "Sent Items" or folder.name == "Отправленные":
            return folder
        for sub_folder in folder.sub_folders:
            result = find_sent_folder(sub_folder)
            if result is not None:
                return result
    except Exception as e:
        print(f"Error searching for Sent folder: {e}")
    return None

def main(pst_file, json_file):

    # Проверяем наличие файла
    if not os.path.exists(pst_file):
        raise FileNotFoundError(f"File not found: {pst_file}")

    pst = pypff.file()
    pst.open(pst_file)

    root_folder = pst.get_root_folder()

    sent_folder = find_sent_folder(root_folder)

    print('Найдена папка:',sent_folder.name)
    all_messages = process_folder(sent_folder)


    # Сохраняем данные в JSON файл
    with open(json_file, "w", encoding='utf-8') as f:
        json.dump(all_messages, f, ensure_ascii=False, indent=4)

    pst.close()
    return json_file

# пример использования
if __name__=="__main__":
        # Открываем PST файл
    # pst_file = "base/input/2024/scat2024.pst"
    pst_file = r'd:\Documents\Coding\Freelancing\NoNameCompany\base\input\2024\scat2024.pst'
    json_file = r'd:\Documents\Coding\Freelancing\NoNameCompany\base\input\emails.json'
    main(pst_file, json_file)