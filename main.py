import os
import json
import httpx
import base64
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

# 🔑 सीक्रेट चाबियां
API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# जेमिनी क्लाइंट
client = genai.Client(api_key=API_KEY)

# 📦 सुपाबेस कनेक्शन
async def query_supabase(path: str, method: str = "GET", json_data: dict = None):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" if method == "POST" else ""
    }
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{path}"
    async with httpx.AsyncClient() as client_http:
        try:
            if method == "GET":
                res = await client_http.get(url, headers=headers, timeout=5.0)
            elif method == "POST":
                res = await client_http.post(url, headers=headers, json=json_data, timeout=5.0)
            elif method == "PATCH":
                res = await client_http.patch(url, headers=headers, json=json_data, timeout=5.0)
            return res.json() if res.status_code in [200, 201] else []
        except Exception:
            return []

@app.get("/", response_class=HTMLResponse)
async def home():
    settings = await query_supabase("site_settings?select=key,value")
    data_dict = {item['key']: item['value'] for item in settings} if settings else {}
    
    v_count = int(data_dict.get("visitor_count", "0")) + 1
    await query_supabase("site_settings?key=eq.visitor_count", "PATCH", {"value": str(v_count)})
    
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AgriDairy Expert AI</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap" rel="stylesheet">
            <style>
                * { box-sizing: border-box; font-family: 'Google Sans', Arial, sans-serif; }
                
                /* 🌌 प्रीमियम डार्क थीम इंटरफेस */
                body { background-color: #131314; margin: 0; padding-bottom: 85px; height: 100vh; display: flex; flex-direction: column; color: #e3e3e3; }
                
                .header { background-color: #131314; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2d2f31; }
                .brand-title { font-size: 20px; font-weight: 500; color: #e3e3e3; }
                
                .auth-btn { background-color: #2e3135; color: #e3e3e3; border: none; padding: 10px 24px; border-radius: 100px; font-size: 14px; cursor: pointer; font-weight: 500; transition: background 0.2s; }
                .auth-btn:hover { background-color: #3c4043; }
                
                .ad-placeholder { background-color: #1e1f20; color: #9aa0a6; text-align: center; padding: 10px; font-size: 12px; margin: 8px auto; max-width: 750px; width: 95%; border-radius: 8px; border: 1px solid #2d2f31; }
                
                .page-content { flex: 1; display: none; overflow-y: auto; padding: 20px; max-width: 750px; width: 100%; margin: 0 auto; }
                .active-page { display: flex; flex-direction: column; }
                
                /* 💬 एडवांस डार्क चैट बबल्स */
                .chat-container { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 24px; padding-bottom: 40px; }
                .message { max-width: 85%; font-size: 16px; line-height: 1.6; word-wrap: break-word; color: #e3e3e3; }
                
                .user-message { background-color: #2b2a2a; padding: 12px 20px; border-radius: 20px; align-self: flex-end; border: 1px solid #3c4043; }
                .ai-message { background-color: transparent; align-self: flex-start; white-space: pre-wrap; padding: 0; }
                .chat-img { max-width: 250px; border-radius: 16px; margin-top: 8px; display: block; border: 1px solid #3c4043; }
                
                /* 🚀 डार्क इनपुट बार */
                .input-container { background: transparent; padding: 15px; display: flex; justify-content: center; position: fixed; bottom: 65px; left: 0; right: 0; z-index: 5; }
                .input-box { max-width: 750px; width: 100%; display: flex; gap: 8px; align-items: center; background: #1e1f20; padding: 8px 16px; border-radius: 100px; border: 1px solid #2d2f31; }
                input[type="text"] { flex: 1; padding: 10px 12px; border: none; font-size: 16px; outline: none; background: transparent; color: #e3e3e3; }
                input[type="text"]::placeholder { color: #8e918f; }
                
                .icon-btn { background: transparent; border: none; width: 40px; height: 40px; border-radius: 50%; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #c4c7c5; }
                .icon-btn:hover { background: #2e3135; }
                .send-btn { background: transparent; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 20px; color: #e3e3e3; }
                
                /* 📊 डार्क कार्ड्स और टेबल्स */
                .info-card { background: #1e1f20; padding: 24px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #2d2f31; }
                .info-card h3 { margin-top: 0; color: #e3e3e3; font-size: 18px; font-weight: 500; }
                table { width: 100%; border-collapse: collapse; margin-top: 16px; }
                th, td { padding: 14px; text-align: left; font-size: 15px; border-bottom: 1px solid #2d2f31; color: #e3e3e3; }
                th { color: #8e918f; font-weight: 500; }
                
                /* 📱 डार्क बॉटम नेविगेशन */
                .nav-bar { background-color: #131314; border-top: 1px solid #2d2f31; position: fixed; bottom: 0; left: 0; right: 0; height: 65px; display: flex; justify-content: space-around; align-items: center; z-index: 10; }
                .nav-item { background: none; border: none; color: #8e918f; display: flex; flex-direction: column; align-items: center; font-size: 11px; cursor: pointer; font-weight: 500; gap: 4px; }
                .nav-item.active { color: #ffffff; font-weight: 700; }
                .nav-icon { font-size: 22px; }
                
                .dashboard-counter { background: #1e1f20; color: #e3e3e3; padding: 14px; text-align: center; font-size: 14px; font-weight: 500; margin-bottom: 20px; border-radius: 12px; border: 1px solid #2d2f31; }
                .admin-section { background: #131314; padding: 20px; border-radius: 16px; border: 1px solid #2d2f31; margin-bottom: 20px; }
                .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); justify-content: center; align-items: center; z-index: 100; }
                .modal-content { background: #1e1f20; padding: 32px; border-radius: 24px; width: 90%; max-width: 360px; text-align: center; border: 1px solid #2d2f31; }
                .modal-input { width: 100%; padding: 14px; margin: 12px 0; border: 1px solid #2d2f31; border-radius: 12px; font-size: 15px; outline: none; background: #131314; color: #e3e3e3; }
                
                /* 🌊 एनिमेटेड लोडिंग बार */
                .gemini-loader { display: none; width: 100%; height: 3px; background: linear-gradient(to right, #4285f4, #34a853, #fbbc05, #ea4335); background-size: 400% 400%; animation: shimmer 1.5s linear infinite; position: fixed; bottom: 145px; left: 0; z-index: 100; }
                @keyframes shimmer { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
            </style>
        </head>
        <body>

            <div class="header">
                <div class="brand-title">AgriDairy Expert AI</div>
                <button class="auth-btn" id="authBtn" onclick="handleAuth
