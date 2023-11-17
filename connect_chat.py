import requests
def get_generations_gpt3(data):
    url = "http://127.0.0.1:5000/chat"  # 替换为实际的API服务器地址
    response = requests.post(url, json=data)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        generated_response = response_data
    else:
        print("API Request Failed with Status Code:", response.status_code)
    return generated_response

if __name__=="__main__":
    get_generations(['hallo','everyone'])
