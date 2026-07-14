"""第三方 API 调用：Open-Meteo 免费天气 API —— 演示 httpx 超时、错误处理"""

import httpx

# 不用 API Key，完全免费
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


async def get_weather(city: str) -> dict:
    """
    调用 Open-Meteo 免费天气接口。
    - 无需 API Key（演示无鉴权 API 调用）
    - 超时：5 秒无响应则降级
    - 错误：非 200 状态码不崩溃，返回兜底数据
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 第一步：城市名 → 经纬度
            geo_resp = await client.get(GEO_URL, params={"name": city, "count": 1, "language": "zh"})

            if geo_resp.status_code != 200:
                return {"status": "error", "message": f"地理编码服务异常 (code={geo_resp.status_code})"}

            geo_data = geo_resp.json()
            results = geo_data.get("results", [])
            if not results:
                return {"status": "not_found", "message": f"未找到城市: {city}"}

            lat = results[0]["latitude"]
            lon = results[0]["longitude"]
            city_name = results[0].get("name", city)

            # 第二步：经纬度 → 天气
            weather_resp = await client.get(
                WEATHER_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True,
                },
            )

            if weather_resp.status_code != 200:
                return {"status": "error", "message": f"天气服务异常 (code={weather_resp.status_code})"}

            data = weather_resp.json()
            current = data.get("current_weather", {})

            return {
                "city": city_name,
                "temperature": current.get("temperature", "N/A"),
                "wind_speed": current.get("windspeed", "N/A"),
                "wind_direction": current.get("winddirection", "N/A"),
                "weather_code": current.get("weathercode", "N/A"),
            }

    except httpx.TimeoutException:
        return {"status": "unavailable", "message": "天气服务请求超时"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
