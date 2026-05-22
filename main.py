import os
import json
import httpx
import base64
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI(title="Vortex.AI Official")

API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None

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
            return res.json() if res.status_code in [200, 201] else []
        except Exception:
            return []

@app.get("/", response_class=HTMLResponse)
async def home():
    html_content = """<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Vortex.AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: 'Google Sans', Arial, sans-serif; margin: 0; padding: 0; }
        body { background-color: #131314; color: #e3e3e3; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        .header { background-color: #131314; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2d2f31; }
        .brand-title { font-size: 22px; font-weight: 400; color: #e3e3e3; letter-spacing: -0.5px; }
        .main-workspace { flex: 1; overflow-y: auto; padding: 20px; max-width: 780px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; }
        .chat-container { display: flex; flex-direction: column; gap: 32px; padding-bottom: 140px; width: 100%; }
        .welcome-center { text-align: center; margin: auto; padding: 40px 20px; }
        .welcome-center h1 { font-size: 36px; font-weight: 400; background: linear-gradient(to right, #4285f4, #9b51e0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 12px; }
        .welcome-center p { color: #8e918f; font-size: 16px; }
        .message-wrapper { display: flex; flex-direction: column; width: 100%; }
        .message { font-size: 16px; line-height: 1.6; word-wrap: break-word; color: #e3e3e3; animation: fadeIn 0.2s ease; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .user-wrapper { align-items: flex-end; }
        .user-message { background-color: #2a2b2d; padding: 12px 20px; border-radius: 20px; border: 1px solid #3c4043; max-width: 85%; }
        .ai-wrapper { align-items: flex-start; }
        .ai-message { background-color: transparent; white-space: pre-wrap; width: 100%; padding-left: 2px; }
        .chat-img { max-width: 280px; border-radius: 14px; margin-top: 12px; display: block; border: 1px solid #3c4043; }
        .input-anchor { background: linear-gradient(to top, #131314 70%, transparent); padding: 20px 15px; position: fixed; bottom: 0; left: 0; right: 0; display: flex; justify-content: center; z-index: 10; }
        .input-capsule { max-width: 780px; width: 100%; display: flex; gap: 6px; align-items: center; background: #1e1f20; padding: 6px 16px; border-radius: 100px; border: 1px solid #2d2f31; }
        input[type="text"] { flex: 1; padding: 12px 6px; border: none; font-size: 16px; outline: none; background: transparent; color: #e3e3e3; }
        input[type="text"]::placeholder { color: #8e918f; }
        .svg-btn { background: transparent; border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; fill: #c4c7c5; transition: background 0.2s; }
        .svg-btn:hover { background: #2e3135; fill: #ffffff; }
        .wave-loader { display: none; width: 100%; height: 3px; background: linear-gradient(to right, #4285f4, #34a853, #fbbc05, #ea4335); background-size: 400% 400%; animation: waveMove 1.5s linear infinite; position: fixed; bottom: 88px; left: 0; z-index: 100; }
        @keyframes waveMove { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    </style>
</head>
<body>
    <div class="header">
        <div class="brand-title">Vortex.AI</div>
    </div>
    <div class="wave-loader" id="shimmerLoader"></div>
    <div class="main-workspace">
        <div class="welcome-center" id="welcomeCore">
            <h1>नमस्ते, मैं Vortex.AI हूँ</h1>
            <p>मैं लाइव इंटरनेट सर्च और विज़न क्षमता से लैस हूँ। आज मैं आपकी क्या मदद कर सकता हूँ?</p>
        </div>
        <div class="chat-container" id="chatScreen" style="display: none;"></div>
    </div>
    <div class="input-anchor">
        <div class="input-capsule">
            <input type="file" id="cameraTrigger" accept="image/*" style="display: none;" onchange="compileImage(this)">
            <button class="svg-btn" onclick="document.getElementById('cameraTrigger').click()">
                <svg viewBox="0 -960 960 960" width="24" height="24"><path d="M480-360q50 0 85-35t35-85q0-50-35-85t-85-35q-50 0-85 35t-35 85q0 50 35 85t85 35Zm0-72q-20 0-34-14t-14-34q0-20 14-34t34-14q20 0 34 14t14 34q0 20-14 34t-34 14ZM160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h144l64-80h224l64 80h144q33 0 56.5 23.5T880-720v480q0-33-23.5 56.5T800-160H160Z"/></svg>
            </button>
            <button class="svg-btn" id="micTrigger" onclick="processVoice()">
                <svg viewBox="0 -960 960 960" width="24" height="24"><path d="M480-400q-50 0-85-35t-35-85v-240q0-50 35-85t85-35q50 0 85 35t35 85v240q0 50-35 85t-85 35Zm0-240ZM440-120v-112q-104-14-172-93t-68-195h80q0 83 58.5 141.5T480-320q83 0 141.5-58.5T680-520h80q0 116-68 195t-172 93v112h-80Z"/></svg>
            </button>
            <input type="text" id="queryBox" placeholder="यहाँ संदेश लिखें..." onkeypress="if(event.key==='Enter') executeVortexAI()">
            <button class="svg-btn" onclick="executeVortexAI()">
                <svg viewBox="0 0 24 24" width="24" height="24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    </div>
    <script>
        let imgPayload = "";
        // वॉइस और इमेज कंपाइलर कोड स्थिर रहेगा
        function processVoice() {
            window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if(!window.SpeechRecognition) { alert("माइक अनुपलब्ध।"); return; }
            const rec = new SpeechRecognition(); rec.lang = 'hi-IN';
            document.getElementById('micTrigger').style.fill = "#ea4335";
            rec.onresult = (e) => { document.getElementById('queryBox').value = e.results[0][0].transcript; };
            rec.onend = () => { document.getElementById('micTrigger').style.fill = "#c4c7c5"; };
            rec.start();
        }
        function compileImage(input) {
            const file = input.files[0]; if(!file) return;
            const reader = new FileReader();
            reader.onload = function(e) { imgPayload = e.target.result.split(',')[1]; alert('📷 फोटो रेडी है!'); };
            reader.readAsDataURL(file);
        }
        async function executeVortexAI() {
            let field = document.getElementById('queryBox'); let q = field.value.trim();
            let screen = document.getElementById('chatScreen'); let core = document.getElementById('welcomeCore');
            if(!q && !imgPayload) return;
            core.style.display = 'none'; screen.style.display = 'flex';
            document.getElementById('shimmerLoader').style.display = 'block';
            let uWrap = document.createElement('div'); uWrap.className = 'message-wrapper user-wrapper';
            let uMsg = document.createElement('div'); uMsg.className = 'message user-message'; uMsg.innerText = q || "📷 फोटो";
            if(imgPayload) { let p = document.createElement('img'); p.className = 'chat-img'; p.src = "data:image/jpeg;base64,"+imgPayload; uMsg.appendChild(p); }
            uWrap.appendChild(uMsg); screen.appendChild(uWrap); field.value = ''; screen.scrollTop = screen.scrollHeight;
            try {
                let response = await fetch('/chat_pro', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ query: q, image_base64: imgPayload })
                });
                let data = await response.json(); imgPayload = "";
                let aiWrap = document.createElement('div'); aiWrap.className = 'message-wrapper ai-wrapper';
                let aiMsg = document.createElement('div'); aiMsg.className = 'message ai-message';
                aiMsg.innerText = data.response; aiWrap.appendChild(aiMsg); screen.appendChild(aiWrap);
            } catch(e) {
                let aiWrap = document.createElement('div'); aiWrap.className = 'message-wrapper ai-wrapper';
                let aiMsg = document.createElement('div'); aiMsg.className = 'message ai-message';
                aiMsg.innerText = "सिस्टम व्यस्त है भाई, कृपया एक बार दोबारा प्रयास करें।";
                aiWrap.appendChild(aiMsg); screen.appendChild(aiWrap);
            }
            document.getElementById('shimmerLoader').style.display = 'none'; screen.scrollTop = screen.scrollHeight;
        }
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

@app.post("/chat_pro")
async def chat_pro(req: Request):
    try:
        body = await req.json()
        query = body.get("query", "")
        image_base64 = body.get("image_base64")
        
        system_instruction = (
            "You are Vortex.AI, a premium, world-class artificial intelligence system built for extreme computational and logical tasking. "
            "You provide highly sophisticated, precise, and scientifically accurate responses. "
            "Always rely on the integrated Google Search tool for ground-truth reality and current affairs data. "
            "Respond naturally in Hindi or Hinglish based on user preference."
        )
        
        contents = []
        if query:
            contents.append(query)
        if image_base64:
            try:
                image_bytes = base64.b64decode(image_base64)
                contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
            except Exception:
                return {"response": "फाइल एरर।"}

        if not client:
            return {"response": "Vortex API Core Error: GEMINI_API_KEY Missing."}

        res = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2
            )
        )
        return {"response": res.text}
    except Exception as e:
        # 🛡️ सुंदर सुरक्षा कवच: लंबा कोड दिखाने के बजाय साफ हिंदी संदेश
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            return {"response": "Vortex.AI अभी बहुत तेज़ी से सोच रहा है भाई! गूगल की फ्री स्पीड लिमिट हिट हुई है। कृपया केवल 5 सेकंड रुककर दोबारा संदेश भेजें, यह तुरंत काम करेगा।"}
        return {"response": f"Vortex इंजन शांत है। कृपया पुनः प्रयास करें।"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
