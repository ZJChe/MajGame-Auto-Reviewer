import requests
from pypinyin import lazy_pinyin

def chinese_to_pinyin(text):
    return ''.join(lazy_pinyin(text))

def get_weather(city_name, api_key="b5ccb8f5b307bc3a7c20c371da871062", lang="zh_cn"):
    city_name_pinyin = chinese_to_pinyin(city_name)
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name_pinyin,
        "appid": api_key,
        "units": "metric",  # 摄氏度
        "lang": lang        # 中文输出
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        return (f"{city_name} 当前天气：{weather_desc}，温度：{temp}℃，"
                f"体感温度：{feels_like}℃，湿度：{humidity}% ，"
                f"风速：{wind_speed} m/s")
        
    except requests.exceptions.HTTPError as e:
        return f"请求失败"
    except KeyError:
        return "无法获取天气信息，请检查城市名称是否正确。"

if __name__ == "__main__":
    city_name = input("请输入城市名称：")
    print(get_weather(city_name))
