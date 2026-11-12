import requests
import json
import time

text = input("Введите слово:  ")
TOKEN = input("Ввести токен:  ")

HEADERS = {"Authorization": f"OAuth {TOKEN}"}
URL_CATS = f"https://cataas.com/cat/cute/says/{text}"


response_create = requests.put(
  "https://cloud-api.yandex.net/v1/disk/resources",           # 1. Создаем папку на Яндекс Диске 
  params={"path": "/SPD-162"},
  headers=HEADERS,
)

response_create.raise_for_status()

response_upload = requests.post(
  "https://cloud-api.yandex.net/v1/disk/resources/upload",    # 2.  Загружаем картинку на Яндекс Диск
  params={"path": f"/SPD-162/{text}.jpg",                     #  не забывать добавлять формат файла (.jpg)
          "url": f"https://cataas.com/cat/cute/says/{text}",
          "overwrite": "true"},
  headers=HEADERS
  )

response_upload.raise_for_status()

status_url = response_upload.json().get("href")   # Ссылка для проверки статуса скачивания и проверка статуса загрузки файла
                                                  # (Тут я понял почему возникает ошибка при попытке получить информацию
                                                  #  о загруженном файле, но не понял как решить проблему... помог ИИ)

while True:
  status_response = requests.get(                 # Блок для проверки статуса скачанного файла (дело рук ИИ)
    status_url, 
    headers=HEADERS
    )    
  status_data = status_response.json()                          

  if status_data.get("status") == "success":
    break
  elif status_data.get("status") == "failed":
    raise Exception("Не получилось скачать файл по указанному URL")

  time.sleep(2)


response_get = requests.get(
  "https://cloud-api.yandex.net/v1/disk/resources",        # 3. Получаем информаци о загруженной картинке 
  params={"path": f"/SPD-162/{text}.jpg"},
  headers=HEADERS
)

response_get.raise_for_status()

json_jpg = response_get.json()                            # 4. Извлекаем из json нужныую информацию (размер картинки)
size = json_jpg["size"]                                   #    и создаем словарь с нужной информацией.
json_dict = {"size": size}


json_string = json.dumps(json_dict, ensure_ascii=False, indent=4)   # Делаем из словаря json файл.

get_url_json = requests.get(
  "https://cloud-api.yandex.net/v1/disk/resources/upload",       # 5. Получаем ссылку для загрузки json фавйла на Яндекс диск
  params={"path": "/SPD-162/size_dict.json",                     
          "overwrite": "true"},
  headers=HEADERS
  
  )

get_url_json.raise_for_status()

url_ugload = get_url_json.json().get("href")      # получаем ссылку из ответа

response_upload_json = requests.put(              # Отправляем наш виртуальный json файл  из оперативной памяти на Яндекс диск.
  url_ugload, data=json_string.encode('utf-8')    
)

response_upload_json.raise_for_status()

  