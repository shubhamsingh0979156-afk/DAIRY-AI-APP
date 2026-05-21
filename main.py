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

# जेमिनी क्लाइंट चालू करें
client = genai.Client(api_key=API_KEY)

# 📦 सुपाबेस डेटाबेस कनेक्शन फंक्शन
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
            <title>AgriDairy Expert Pro</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap" rel="stylesheet">
            <style>
                * { box-sizing: border-box; font-family: 'Google Sans', Arial, sans-serif; }
                
                /* 💻 शुद्ध Google Gemini थीम (सफ़ेद, साफ़ और बिना फालतू कलर्स के) */
                body { background-color: #ffffff; margin: 0; padding-bottom: 85px; height: 100vh; display: flex; flex-direction: column; color: #1f1f1f; }
                
                .header { background-color: #ffffff; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f3f4; }
                .brand-title { font-size: 22px; font-weight: 500; color: #1f1f1f; letter-spacing: -0.5px; }
                
                .auth-btn { background-color: #f1f3f4; color: #1f1f1f; border: none; padding: 10px 24px; border-radius: 100px; font-size: 14px; cursor: pointer; font-weight: 500; transition: background 0.2s; }
                .auth-btn:hover { background-color: #e8eaed; }
                
                .ad-placeholder { background-color: #f8f9fa; color: #70757a; text-align: center; padding: 10px; font-size: 12px; margin: 8px auto; max-width: 750px; width: 95%; border-radius: 8px; border: 1px solid #f1f3f4; }
                
                .page-content { flex: 1; display: none; overflow-y: auto; padding: 20px; max-width: 750px; width: 100%; margin: 0 auto; }
                .active-page { display: flex; flex-direction: column; }
                
                /* 💬 जेमिनी स्टाइल चैट लेआउट (बिना किसी बैकग्राउंड डिब्बों के, साफ़ टेक्स्ट और यूज़र बबल) */
                .chat-container { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 24px; padding-bottom: 40px; }
                .message { max-width: 85%; font-size: 16px; line-height: 1.6; word-wrap: break-word; animation: fadeIn 0.2s ease; color: #1f1f1f; }
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                
                /* यूज़र का मैसेज हल्के ग्रे डिब्बे में दाईं तरफ */
                .user-message { background-color: #f1f3f4; padding: 12px 20px; border-radius: 20px; align-self: flex-end; }
                /* एआई का जवाब बिना किसी बैकग्राउंड के सीधे साफ़ टेक्स्ट में बाईं तरफ (जैसे असली जेमिनी में होता है) */
                .ai-message { background-color: transparent; align-self: flex-start; white-space: pre-wrap; padding: 0; }
                .chat-img { max-width: 250px; border-radius: 16px; margin-top: 8px; display: block; border: 1px solid #e8eaed; }
                
                /* 🚀 जेमिनी जैसा राउंडेड इनपुट बार जो स्क्रीन पर तैरता है */
                .input-container { background: transparent; padding: 15px; display: flex; justify-content: center; position: fixed; bottom: 65px; left: 0; right: 0; z-index: 5; }
                .input-box { max-width: 750px; width: 100%; display: flex; gap: 8px; align-items: center; background: #f1f3f4; padding: 8px 16px; border-radius: 100px; transition: background 0.2s; }
                .input-box:focus-within { background: #e8eaed; }
                input[type="text"] { flex: 1; padding: 10px 12px; border: none; font-size: 16px; outline: none; background: transparent; color: #1f1f1f; }
                
                .icon-btn { background: transparent; border: none; width: 40px; height: 40px; border-radius: 50%; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #444746; transition: background 0.2s; }
                .icon-btn:hover { background: rgba(0,0,0,0.05); }
                .send-btn { background: transparent; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 20px; color: #1f1f1f; }
                
                /* 📊 मिनिमल कार्ड्स और टेबल्स */
                .info-card { background: #ffffff; padding: 24px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #f1f3f4; }
                .info-card h3 { margin-top: 0; color: #1f1f1f; font-size: 18px; font-weight: 500; }
                table { width: 100%; border-collapse: collapse; margin-top: 16px; }
                th, td { padding: 14px; text-align: left; font-size: 15px; border-bottom: 1px solid #f1f3f4; }
                th { color: #70757a; font-weight: 500; background: none; }
                
                /* 📱 साफ़ सुथरा बॉटम नेविगेशन */
                .nav-bar { background-color: #ffffff; border-top: 1px solid #f1f3f4; position: fixed; bottom: 0; left: 0; right: 0; height: 65px; display: flex; justify-content: space-around; align-items: center; z-index: 10; }
                .nav-item { background: none; border: none; color: #70757a; display: flex; flex-direction: column; align-items: center; font-size: 11px; cursor: pointer; font-weight: 500; gap: 4px; }
                .nav-item.active { color: #1f1f1f; font-weight: 700; }
                .nav-icon { font-size: 22px; }
                
                .dashboard-counter { background: #f8f9fa; color: #1f1f1f; padding: 14px; text-align: center; font-size: 14px; font-weight: 500; margin-bottom: 20px; border-radius: 12px; border: 1px solid #f1f3f4; }
                .admin-section { background: #ffffff; padding: 20px; border-radius: 16px; border: 1px solid #f1f3f4; margin-bottom: 20px; }
                .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.3); justify-content: center; align-items: center; z-index: 100; backdrop-filter: blur(2px); }
                .modal-content { background: white; padding: 32px; border-radius: 24px; width: 90%; max-width: 360px; text-align: center; }
                .modal-input { width: 100%; padding: 14px; margin: 12px 0; border: 1px solid #chchch; border-radius: 12px; font-size: 15px; outline: none; background: #f8f9fa; }
                
                /* 🌊 जेमिनी जैसा पतला प्रोग्रेस बार */
                .gemini-loader { display: none; width: 100%; height: 3px; background: linear-gradient(to right, #4285f4, #34a853, #fbbc05, #ea4335); background-size: 400% 400%; animation: shimmer 1.5s linear infinite; position: fixed; bottom: 145px; left: 0; z-index: 100; }
                @keyframes shimmer { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
            </style>
        </head>
        <body>

            <div class="header">
                <div class="brand-title">Gemini AgriDairy</div>
                <button class="auth-btn" id="authBtn" onclick="handleAuthClick()">लॉगिन</button>
            </div>
            
            <div class="ad-placeholder">Google Ads यहाँ दिखाई देंगे</div>
            <div class="gemini-loader" id="globalSpinner"></div>

            <div id="welcomePage" class="page-content active-page" style="text-align: center; padding-top: 80px;">
                <h2 style="font-weight:400; font-size:28px; margin-bottom:10px;">नमस्ते, मैं आपका डेयरी गाइड हूँ</h2>
                <p style="color: #70757a; font-size: 16px; padding: 0 40px; line-height:1.6; margin-bottom:30px;">पशुओं के स्वास्थ्य, रोगों के सटीक इलाज या दूध डायरी का हिसाब रखने के लिए सुरक्षित शुरुआत करें।</p>
                <button class="auth-btn" style="background-color:#1f1f1f; color:white; padding:14px 40px;" onclick="handleAuthClick()">लॉगिन करें</button>
            </div>

            <div id="chatPage" class="page-content">
                <div class="chat-container" id="chatContainer">
                    <div class="message ai-message">राम-राम भाई! मैं आपका जेमिनी डेयरी एक्सपर्ट हूँ। पशुपालन या बीमारियों से जुड़ा कोई भी सवाल पूछें, या नीचे कैमरा बटन दबाकर सीधे फोटो भेजें।</div>
                </div>
                <div class="input-container">
                    <div class="input-box">
                        <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="handleImageUpload(this)">
                        <button class="icon-btn" onclick="document.getElementById('imageInput').click()">📷</button>
                        <button class="icon-btn" id="micBtn" onclick="startVoiceRecognition()">🎤</button>
                        <input type="text" id="query" placeholder="यहाँ संदेश लिखें..." onkeypress="if(event.key === 'Enter') askAI()">
                        <button class="send-btn" onclick="askAI()">➔</button>
                    </div>
                </div>
            </div>

            <div id="ratePage" class="page-content">
                <div class="info-card">
                    <h3>📈 ताज़ा बाज़ार और मंडी भाव</h3>
                    <table>
                        <tr><th>वस्तु (Item)</th><th>भाव (Price)</th></tr>
                        <tr><td>गाय का दूध (प्रति लीटर - 4.0 Fat)</td><td id="lbl_cow" style="font-weight:700;">COW_RATE_PLACEHOLDER</td></tr>
                        <tr><td>भैंस का दूध (प्रति लीटर - 6.5 Fat)</td><td id="lbl_buff" style="font-weight:700;">BUFF_RATE_PLACEHOLDER</td></tr>
                        <tr><td>सरसों खली (प्रति क्विंटल)</td><td id="lbl_must">MUST_RATE_PLACEHOLDER</td></tr>
                        <tr><td>पशु आहार/फीड (50KG बैग)</td><td id="lbl_bag">BAG_RATE_PLACEHOLDER</td></tr>
                    </table>
                </div>
            </div>

            <div id="dairyPage" class="page-content">
                <div class="info-card">
                    <h3>📋 नया पशु रिकॉर्ड जोड़ें</h3>
                    <div style="display:flex; gap:12px; margin-bottom:12px;">
                        <input type="text" id="cattleName" class="modal-input" placeholder="गाय/भैंस का नाम या नंबर" style="flex:1; margin:0;">
                        <select id="cattleType" style="padding:12px; border-radius:12px; border:1px solid #dadce0; background:#ffffff;">
                            <option value="गाय">गाय 🐄</option>
                            <option value="भैंस">भैंस 🐃</option>
                        </select>
                    </div>
                    <label style="font-size:13px; color:#70757a;">संभावित बियाने/AI की तारीख:</label>
                    <input type="date" id="cattleDate" class="modal-input" style="margin-top:6px;">
                    <button class="auth-btn" style="width:100%; background:#1f1f1f; color:white;" onclick="addCattleBackend()">सुरक्षित करें</button>
                    <div id="cattleList" style="margin-top:20px; font-size:15px; line-height:1.6;"></div>
                </div>

                <div class="info-card">
                    <h3>🥛 मासिक दूध डायरी</h3>
                    <div style="display:flex; gap:12px; margin-bottom:12px;">
                        <input type="number" id="milkLitres" placeholder="कुल लीटर दूध" class="modal-input" style="width:50%; margin:0;">
                        <input type="number" id="milkFat" placeholder="फैट (Fat)" class="modal-input" style="width:50%; margin:0;">
                    </div>
                    <button class="auth-btn" style="width:100%; background:#1f1f1f; color:white;" onclick="addMilkBackend()">हिसाब जोड़ें</button>
                    <div id="milkResult" style="margin-top:15px; font-weight:700;"></div>
                </div>
            </div>

            <div id="schemePage" class="page-content">
                <div class="info-card">
                    <h3 id="lbl_sch_title" style="font-size:20px; font-weight:500;">SCHEME_TITLE_PLACEHOLDER</h3>
                    <p id="lbl_sch_detail" style="line-height:1.7; color:#4a4a4a; font-size:16px;">SCHEME_DETAIL_PLACEHOLDER</p>
                </div>
            </div>

            <div id="adminPage" class="page-content">
                <div class="dashboard-counter">
                    👑 एडमिन डैशबोर्ड | कुल विज़िटर्स: VISITOR_COUNT_PLACEHOLDER
                </div>
                <div class="admin-section">
                    <h4>🔄 मंडी रेट अपडेट करें</h4>
                    <input type="text" id="txt_cow" class="modal-input" placeholder="गाय दूध का नया रेट">
                    <input type="text" id="txt_buff" class="modal-input" placeholder="भैंस दूध का नया रेट">
                    <button class="auth-btn" style="background:#1f1f1f; color:white;" onclick="updateRatesBackend()">मंडी रेट बदलें</button>
                </div>
                <div class="admin-section">
                    <h4>🔄 सरकारी योजना बदलें</h4>
                    <input type="text" id="txt_sch_title" class="modal-input" placeholder="योजना का नाम">
                    <textarea id="txt_sch_detail" class="modal-input" placeholder="योजना की पूरी डिटेल लिखें" style="height:100px; font-family:inherit; border-radius:12px; border:1px solid #dadce0; padding:12px; width:100%; outline:none; background:#ffffff;"></textarea>
                    <button class="auth-btn" style="background:#1f1f1f; color:white; margin-top:12px;" onclick="updateSchemeBackend()">योजना अपलोड करें</button>
                </div>
            </div>

            <div class="nav-bar" id="bottomNav" style="display:none;">
                <button class="nav-item active" id="btn-chat" onclick="switchPage('chatPage', 'btn-chat')">
                    <span class="nav-icon">💬</span><span>चैट</span>
                </button>
                <button class="nav-item" id="btn-rate" onclick="switchPage('ratePage', 'btn-rate')">
                    <span class="nav-icon">📈</span><span>मंडी रेट</span>
                </button>
                <button class="nav-item" id="btn-dairy" onclick="switchPage('dairyPage', 'btn-dairy')">
                    <span class="nav-icon">📝</span><span>मेरी डेयरी</span>
                </button>
                <button class="nav-item" id="btn-scheme" onclick="switchPage('schemePage', 'btn-scheme')">
                    <span class="nav-icon">📜</span><span>योजनाएं</span>
                </button>
                <button class="nav-item" id="btn-admin" style="display:none;" onclick="switchPage('adminPage', 'btn-admin')">
                    <span class="nav-icon">👑</span><span>कंट्रोल</span>
                </button>
            </div>

            <div class="modal" id="authModal">
                <div class="modal-content" id="loginBox">
                    <h3 style="font-weight:500; margin-top:0;">लॉगिन</h3>
                    <input type="text" id="username" class="modal-input" placeholder="अपना नाम लिखें">
                    <input type="text" id="userphone" class="modal-input" placeholder="मोबाइल नंबर / एडमिन पासवर्ड">
                    <button class="auth-btn" style="width:100%; background-color:#1f1f1f; color:white; padding:14px; margin-top:10px;" onclick="sendDemoOTP()">OTP भेजें</button>
                    <button class="auth-btn" style="width:100%; margin-top:6px; background:#f1f3f4; color:#1f1f1f;" onclick="closeAuthModal()">बंद करें</button>
                </div>
                <div class="modal-content" id="otpBox" style="display:none;">
                    <h3>🔐 ओटीपी कोड</h3>
                    <p style="font-size:13px; color:#ff6d00;">डेमो OTP '1234' दर्ज करें</p>
                    <input type="number" id="otpInput" class="modal-input" placeholder="4 अंकों का OTP डालें">
                    <button class="auth-btn" style="width:100%; background-color:#1f1f1f; color:white; padding:14px; margin-top:10px;" onclick="verifyDemoOTP()">सत्यापित करें</button>
                </div>
            </div>

            <script>
                let currentUserName = "";
                let currentUserPhone = "";
                let base64ImageStr = "";

                window.onload = function() {
                    let savedPhone = localStorage.getItem("dairy_phone");
                    let savedName = localStorage.getItem("dairy_name");
                    if(savedPhone && savedName) {
                        currentUserName = savedName;
                        currentUserPhone = savedPhone;
                        executeLogin(savedPhone === "Shubham79");
                    }
                };

                function switchPage(pageId, btnId) {
                    document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-page'));
                    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
                    document.getElementById(pageId).classList.add('active-page');
                    if(btnId) document.getElementById(btnId).classList.add('active');
                    
                    if(pageId === 'chatPage') loadChatHistory();
                    if(pageId === 'dairyPage') { loadCattleRecords(); loadMilkRecords(); }
                }

                function handleAuthClick() {
                    if(document.getElementById('authBtn').innerText === "लॉगआऊट") {
                        localStorage.clear();
                        currentUserName = "";
                        currentUserPhone = "";
                        document.getElementById('authBtn').innerText = "लॉगिन";
                        document.getElementById('bottomNav').style.display = 'none';
                        document.getElementById('btn-admin').style.display = 'none';
                        switchPage('welcomePage');
                    } else {
                        document.getElementById('authModal').style.display = 'flex';
                        document.getElementById('loginBox').style.display = 'block';
                        document.getElementById('otpBox').style.display = 'none';
                    }
                }

                function closeAuthModal() { document.getElementById('authModal').style.display = 'none'; }

                function sendDemoOTP() {
                    currentUserName = document.getElementById('username').value.trim();
                    currentUserPhone = document.getElementById('userphone').value.trim();
                    if(!currentUserName || !currentUserPhone) { alert('कृपया पूरा नाम और नंबर भरें!'); return; }
                    
                    if(currentUserPhone === 'Shubham79') {
                        localStorage.setItem("dairy_phone", "Shubham79");
                        localStorage.setItem("dairy_name", "Admin");
                        executeLogin(true);
                        return;
                    }
                    if(currentUserPhone.length < 10) { alert('सही मोबाइल नंबर डालें!'); return; }
                    document.getElementById('loginBox').style.display = 'none';
                    document.getElementById('otpBox').style.display = 'block';
                }

                function verifyDemoOTP() {
                    let otp = document.getElementById('otpInput').value.trim();
                    if(otp === '1234') {
                        localStorage.setItem("dairy_phone", currentUserPhone);
                        localStorage.setItem("dairy_name", currentUserName);
                        executeLogin(false);
                    } else { alert('गलत OTP! 1234 डालें।'); }
                }

                function executeLogin(isAdmin) {
                    closeAuthModal();
                    document.getElementById('bottomNav').style.display = 'flex';
                    document.getElementById('authBtn').innerText = "लॉगआऊट";
                    if(isAdmin) {
                        document.getElementById('btn-admin').style.display = 'flex';
                        switchPage('adminPage', 'btn-admin');
                    } else {
                        document.getElementById('btn-admin').style.display = 'none';
                        switchPage('chatPage', 'btn-chat');
                    }
                }

                function startVoiceRecognition() {
                    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    if(!window.SpeechRecognition) { alert("माइक सपोर्ट नहीं कर रहा है।"); return; }
                    const recognition = new SpeechRecognition();
                    recognition.lang = 'hi-IN';
                    document.getElementById('micBtn').innerText = "🛑";
                    recognition.onresult = (event) => {
                        document.getElementById('query').value = event.results[0][0].transcript;
                    };
                    recognition.onend = () => { document.getElementById('micBtn').innerText = "🎤"; };
                    recognition.start();
                }

                function handleImageUpload(input) {
                    const file = input.files[0];
                    if(!file) return;
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        base64ImageStr = e.target.result.split(',')[1];
                        alert('📷 फोटो अटैच हो गई है! अब सवाल भेजें।');
                    };
                    reader.readAsDataURL(file);
                }

                async function askAI() {
                    let inputField = document.getElementById('query');
                    let q = inputField.value.trim();
                    let chatContainer = document.getElementById('chatContainer');
                    if(!q && !base64ImageStr) return;
                    
                    document.getElementById('globalSpinner').style.display = 'block';
                    
                    let userDiv = document.createElement('div');
                    userDiv.className = 'message user-message';
                    userDiv.innerText = q || "📷 फोटो सेंड की गई";
                    if(base64ImageStr) {
                        let img = document.createElement('img');
                        img.className = 'chat-img';
                        img.src = "data:image/jpeg;base64," + base64ImageStr;
                        userDiv.appendChild(img);
                    }
                    chatContainer.appendChild(userDiv);
                    inputField.value = '';
                    chatContainer.scrollTop = chatContainer.scrollHeight;

                    try {
                        let response = await fetch('/chat_pro', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                phone: currentUserPhone,
                                query: q,
                                image_base64: base64ImageStr
                            })
                        });
                        let data = await response.json();
                        base64ImageStr = "";
                        
                        let aiDiv = document.createElement('div');
                        aiDiv.className = 'message ai-message';
                        aiDiv.innerText = data.response || "जवाब नहीं मिल पाया भाई।";
                        chatContainer.appendChild(aiDiv);
                    } catch(e) {
                        let aiDiv = document.createElement('div');
                        aiDiv.className = 'message ai-message';
                        aiDiv.innerText = 'सर्वर थोड़ा धीमा है, कृपया एक बार दोबारा प्रयास करें भाई।';
                        chatContainer.appendChild(aiDiv);
                    }
                    document.getElementById('globalSpinner').style.display = 'none';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }

                async function loadChatHistory() {
                    let chatContainer = document.getElementById('chatContainer');
                    try {
                        let res = await fetch('/get_chat?phone=' + currentUserPhone);
                        let data = await res.json();
                        if(data && data.length > 0) {
                            chatContainer.innerHTML = "";
                            data.forEach(msg => {
                                let div = document.createElement('div');
                                div.className = msg.sender === 'user' ? 'message user-message' : 'message ai-message';
                                div.innerText = msg.message;
                                chatContainer.appendChild(div);
                            });
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }
                    } catch(e) {}
                }

                async function addCattleBackend() {
                    let name = document.getElementById('cattleName').value.trim();
                    let type = document.getElementById('cattleType').value;
                    let date = document.getElementById('cattleDate').value;
                    if(!name || !date) { alert('पूरी जानकारी भरें!'); return; }
                    
                    await fetch('/add_cattle', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({phone: currentUserPhone, name: name, type: type, date_text: date})
                    });
                    document.getElementById('cattleName').value = "";
                    loadCattleRecords();
                }

                async function loadCattleRecords() {
                    try {
                        let res = await fetch('/get_cattle?phone=' + currentUserPhone);
                        let data = await res.json();
                        let list = document.getElementById('cattleList');
                        list.innerHTML = "<b>सुरक्षित पशु रिकॉर्ड:</b><br>";
                        if(data && data.length > 0) {
                            data.forEach(c => {
                                list.innerHTML += `• <b>${c.name}</b> (${c.type}) - तारीख: ${c.date_text}<br>`;
                            });
                        }
                    } catch(e) {}
                }

                async function addMilkBackend() {
                    let lit = parseFloat(document.getElementById('milkLitres').value);
                    let fat = parseFloat(document.getElementById('milkFat').value);
                    if(!lit || !fat) { alert('सही मात्रा भरें!'); return; }
                    let earn = lit * (fat * 11);
                    
                    await fetch('/add_milk', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({phone: currentUserPhone, litres: lit, fat: fat, earning: earn})
                    });
                    document.getElementById('milkLitres').value = "";
                    document.getElementById('milkFat').value = "";
                    loadMilkRecords();
                }

                async function loadMilkRecords() {
                    try {
                        let res = await fetch('/get_milk?phone=' + currentUserPhone);
                        let data = await res.json();
                        let resDiv = document.getElementById('milkResult');
                        let totalL = 0, totalE = 0;
                        if(data && data.length > 0) {
                            data.forEach(m => { totalL += m.litres; totalE += m.earning; });
                        }
                        resDiv.innerHTML = `🥛 कुल दूध: ${totalL.toFixed(1)} लीटर | 💰 कुल राशि: ₹${totalE.toFixed(2)}`;
                    } catch(e) {}
                }

                async function updateRatesBackend() {
                    let cow = document.getElementById('txt_cow').value.trim();
                    let buff = document.getElementById('txt_buff').value.trim();
                    if(cow) await fetch('/update_setting?key=milk_rate_cow&val=' + encodeURIComponent(cow));
                    if(buff) await fetch('/update_setting?key=milk_rate_buffalo&val=' + encodeURIComponent(buff));
                    alert('मंडी रेट लाइव बदल गया है।');
                }

                async function updateSchemeBackend() {
                    let title = document.getElementById('txt_sch_title').value.trim();
                    let detail = document.getElementById('txt_sch_detail').value.trim();
                    if(title) await fetch('/update_setting?key=scheme_title&val=' + encodeURIComponent(title));
                    if(detail) await fetch('/update_setting?key=scheme_detail&val=' + encodeURIComponent(detail));
                    alert('योजना लाइव हो चुकी है।');
                }
            </script>
        </body>
    </html>
    """
    html_content = html_content.replace("VISITOR_COUNT_PLACEHOLDER", str(v_count))
    html_content = html_content.replace("COW_RATE_PLACEHOLDER", data_dict.get("milk_rate_cow", "₹45"))
    html_content = html_content.replace("BUFF_RATE_PLACEHOLDER", data_dict.get("milk_rate_buffalo", "₹70"))
    html_content = html_content.replace("MUST_RATE_PLACEHOLDER", data_dict.get("feed_rate_mustard", "₹3,000"))
    html_content = html_content.replace("BAG_RATE_PLACEHOLDER", data_dict.get("feed_rate_bag", "₹1,300"))
    html_content = html_content.replace("SCHEME_TITLE_PLACEHOLDER", data_dict.get("scheme_title", "सरकारी योजना"))
    html_content = html_content.replace("SCHEME_DETAIL_PLACEHOLDER", data_dict.get("scheme_detail", "विवरण"))
    
    return html_content

# 🚀 इमेज फिक्स के साथ एडवांस जेमिनी प्रो बैकएंड
@app.post("/chat_pro")
async def chat_pro(req: Request):
    body = await req.json()
    phone = body.get("phone") or "Guest"
    query = body.get("query", "")
    image_base64 = body.get("image_base64")
    
    system_instruction = (
        "तुम 'AgriDairy Expert AI' हो। तुम एक बेहद मददगार और अनुभवी डेयरी साइंस एक्सपर्ट हो। "
        "तुम भारतीय किसानों की भाषा (हिंदी, इंग्लिश, या हिंग्लिश) को तुरंत समझकर आसान भाषा में जवाब देते हो। "
        "जब भी कोई डेयरी का सवाल पूछे या पशु की बीमारी की फोटो भेजे, तुम तुरंत Google Search का उपयोग करोगे "
        "और सटीक वैज्ञानिक डेटा, चारा मात्रा (KG), दवाइयों के नाम और ग्राउंड रिपोर्ट के आधार पर ही उत्तर दोगे।"
    )
    
    contents = []
    if query:
        contents.append(query)
    
    # 📷 नया जेमिनी प्रो इमेज पार्सिंग स्ट्रक्चर जो एरर 400 को खत्म करेगा
    if image_base64:
        try:
            image_bytes = base64.b64decode(image_base64)
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
        except Exception as e:
            return {"response": f"फोटो को समझने में समस्या आई भाई। कृपया दोबारा खींचें।"}

    try:
        res = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2
            )
        )
        ai_response = res.text
        
        # सुपाबेस में चैट सेव करें
        await query_supabase("chat_history", "POST", {"phone": phone, "sender": "user", "message": query or "📷 फोटो अपलोड"})
        await query_supabase("chat_history", "POST", {"phone": phone, "sender": "ai", "message": ai_response})
        
        return {"response": ai_response}
    except Exception as e:
        return {"response": "नमस्ते भाई, इस समय नेटवर्क थोड़ा धीमा है, कृपया एक बार पुनः अपना सवाल भेजें।"}

@app.get("/get_chat")
async def get_chat(phone: str):
    return await query_supabase(f"chat_history?phone=eq.{phone}&order=created_at.asc")

@app.post("/add_cattle")
async def add_cattle(req: Request):
    body = await req.json()
    return await query_supabase("cattle_records", "POST", body)

@app.get("/get_cattle")
async def get_cattle(phone: str):
    return await query_supabase(f"cattle_records?phone=eq.{phone}")

@app.post("/add_milk")
async def add_milk(req: Request):
    body = await req.json()
    return await query_supabase("milk_records", "POST", body)

@app.get("/get_milk")
async def get_milk(phone: str):
    return await query_supabase(f"milk_records?phone=eq.{phone}")

@app.get("/update_setting")
async def update_setting(key: str, val: str):
    return await query_supabase(f"site_settings?key=eq.{key}", "PATCH", {"value": val})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
