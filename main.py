import os
import json
import httpx
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

# 🔑 सभी सीक्रेट चाबियां एन्वायरमेंट (Render Envs) से लोड होंगी
API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# जेमिनी एआई क्लाइंट चालू करें
client = genai.Client(api_key=API_KEY)

# 📦 सुपाबेस डेटाबेस से संपर्क करने के लिए एक मददगार फंक्शन
async def query_supabase(path: str, method: str = "GET", json_data: dict = None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" if method == "POST" else ""
    }
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{path}"
    async with httpx.AsyncClient() as client_http:
        if method == "GET":
            res = await client_http.get(url, headers=headers)
        elif method == "POST":
            res = await client_http.post(url, headers=headers, json=json_data)
        elif method == "PATCH":
            res = await client_http.patch(url, headers=headers, json=json_data)
        return res.json() if res.status_code in [200, 201] else []

@app.get("/", response_class=HTMLResponse)
async def home():
    # 📈 विज़िटर्स काउंटर को डेटाबेस में लाइव बढ़ाएं और ताज़ा डेटा लाएं
    settings = await query_supabase("site_settings?select=key,value")
    data_dict = {item['key']: item['value'] for item in settings}
    
    # अगर पहली बार सेटअप है तो डिफ़ॉल्ट मान सेट करें
    v_count = int(data_dict.get("visitor_count", "0")) + 1
    await query_supabase("site_settings?key=eq.visitor_count", "PATCH", {"value": str(v_count)})
    
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AgriDairy Expert Pro</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { box-sizing: border-box; }
                body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f7f5; margin: 0; padding-bottom: 70px; height: 100vh; display: flex; flex-direction: column; }
                .header { background-color: #1b5e20; color: white; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; font-size: 18px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); z-index: 10; }
                .auth-btn { background-color: #ffff; color: #1b5e20; border: none; padding: 6px 14px; border-radius: 20px; font-size: 14px; cursor: pointer; font-weight: bold; }
                .ad-placeholder { background-color: #f1f3f4; border: 1px dashed #bbb; color: #777; text-align: center; padding: 10px; font-size: 12px; margin: 5px auto; max-width: 800px; width: 95%; border-radius: 5px; }
                .page-content { flex: 1; display: none; overflow-y: auto; padding: 15px; max-width: 800px; width: 100%; margin: 0 auto; }
                .active-page { display: flex; flex-direction: column; }
                .chat-container { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; margin-bottom: 80px; padding-bottom: 20px; }
                .message { max-width: 85%; padding: 12px 16px; border-radius: 18px; font-size: 15px; line-height: 1.5; word-wrap: break-word; }
                .user-message { background-color: #e8f5e9; color: #1b5e20; align-self: flex-end; border-bottom-right-radius: 4px; border: 1px solid #c8e6c9; }
                .ai-message { background-color: white; color: #333; align-self: flex-start; border-bottom-left-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #eee; white-space: pre-wrap; }
                .chat-img { max-width: 100%; border-radius: 10px; margin-top: 5px; display: block; }
                .input-container { background-color: white; padding: 10px; border-top: 1px solid #e0e0e0; display: flex; justify-content: center; position: fixed; bottom: 60px; left: 0; right: 0; z-index: 5; }
                .input-box { max-width: 800px; width: 100%; display: flex; gap: 6px; align-items: center; }
                input[type="text"], input[type="number"], select { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 25px; font-size: 15px; outline: none; background-color: #f9f9f9; }
                .icon-btn { background: #f0f4f1; border: none; width: 42px; height: 42px; border-radius: 50%; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s; }
                .icon-btn:active { background: #c8e6c9; }
                .send-btn { background-color: #1b5e20; color: white; border: none; padding: 12px 22px; border-radius: 25px; cursor: pointer; font-weight: bold; }
                .info-card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 4px solid #1b5e20; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; background: white; }
                th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }
                th { background-color: #e8f5e9; color: #1b5e20; }
                .nav-bar { background-color: white; border-top: 1px solid #e0e0e0; position: fixed; bottom: 0; left: 0; right: 0; height: 60px; display: flex; justify-content: space-around; align-items: center; z-index: 10; }
                .nav-item { background: none; border: none; color: #666; display: flex; flex-direction: column; align-items: center; font-size: 12px; cursor: pointer; font-weight: 500; }
                .nav-item.active { color: #1b5e20; font-weight: bold; }
                .nav-icon { font-size: 18px; margin-bottom: 2px; }
                .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; z-index: 100; }
                .modal-content { background: white; padding: 25px; border-radius: 15px; width: 90%; max-width: 350px; text-align: center; }
                .modal-input { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; }
                .dashboard-counter { background-color: #ffd54f; color: #333; padding: 10px; text-align: center; font-size: 13px; font-weight: bold; margin-bottom: 15px; border-radius: 8px; border: 1px solid #ffa000; }
                .admin-section { background: #fffde7; padding: 15px; border-radius: 10px; border: 1px solid #fff59d; margin-bottom: 15px; }
                .loading-spinner { display: none; width: 24px; height: 24px; border: 3px solid #f3f3f3; border-top: 3px solid #1b5e20; border-radius: 50%; animation: spin 1s linear infinite; margin: 5px auto; }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            </style>
        </head>
        <body>

            <div class="header">
                <div>🐄 AgriDairy Expert Pro</div>
                <button class="auth-btn" id="authBtn" onclick="handleAuthClick()">लॉगिन</button>
            </div>
            
            <div class="ad-placeholder">Google Ads यहाँ दिखाई देंगे (यूज़र को बिना डिस्टर्ब किए)</div>

            <div id="welcomePage" class="page-content active-page" style="text-align: center; padding-top: 40px;">
                <img src="https://img.icons8.com/color/96/cow.png" alt="Cow" style="margin-bottom: 15px;">
                <h2>डिजिटल डेयरी फार्मिंग में आपका स्वागत है!</h2>
                <p style="color: #666; font-size: 15px; padding: 0 20px;">एआई चैट गाइड, पशु रिकॉर्ड, दूध डायरी का हिसाब और मंडी रेट देखने के लिए कृपया ऊपर दिए गए बटन से सुरक्षित लॉगिन करें।</p>
                <button class="send-btn" style="margin-top: 20px; padding: 12px 40px;" onclick="handleAuthClick()">लॉगिन करें</button>
            </div>

            <div id="chatPage" class="page-content">
                <div class="chat-container" id="chatContainer">
                    <div class="message ai-message">राम-राम भाई! मैं आपका डेयरी एक्सपर्ट AI हूँ। पशुपालन या बीमारियों से जुड़ा कोई भी वैज्ञानिक सवाल यहाँ पूछें। आप फोटो खींचकर भी बीमारी पूछ सकते हैं।</div>
                </div>
                <div class="input-container">
                    <div class="input-box">
                        <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="handleImageUpload(this)">
                        <button class="icon-btn" onclick="document.getElementById('imageInput').click()">📷</button>
                        
                        <button class="icon-btn" id="micBtn" onclick="startVoiceRecognition()">🎤</button>
                        
                        <input type="text" id="query" placeholder="यहाँ अपना सवाल लिखें..." onkeypress="if(event.key === 'Enter') askAI()">
                        <button class="send-btn" onclick="askAI()">भेजें</button>
                    </div>
                </div>
                <div class="loading-spinner" id="globalSpinner"></div>
            </div>

            <div id="ratePage" class="page-content">
                <div class="info-card">
                    <h3>📈 ताज़ा दूध और मंडी बाजार भाव</h3>
                    <table>
                        <tr><th>वस्तु (Item)</th><th>ताज़ा रेट (Price)</th></tr>
                        <tr><td>गाय का दूध (प्रति लीटर - 4.0 Fat)</td><td id="lbl_cow">COW_RATE_PLACEHOLDER</td></tr>
                        <tr><td>भैंस का दूध (प्रति लीटर - 6.5 Fat)</td><td id="lbl_buff">BUFF_RATE_PLACEHOLDER</td></tr>
                        <tr><td>सरसों खली (प्रति क्विंटल)</td><td id="lbl_must">MUST_RATE_PLACEHOLDER</td></tr>
                        <tr><td>पशु आहार/फीड (50KG बैग)</td><td id="lbl_bag">BAG_RATE_PLACEHOLDER</td></tr>
                    </table>
                </div>
            </div>

            <div id="dairyPage" class="page-content">
                <div class="info-card">
                    <h3>📋 पशु रिकॉर्ड जोड़ें</h3>
                    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
                        <input type="text" id="cattleName" class="modal-input" placeholder="गाय/भैंस का नाम या टैग नंबर" style="flex:1;">
                        <select id="cattleType" style="padding:10px; border-radius:8px; border:1px solid #ccc;">
                            <option value="गाय">गाय 🐄</option>
                            <option value="भैंस">भैंस 🐃</option>
                        </select>
                    </div>
                    <label style="font-size:12px; color:#666;">संभावित बियाने/AI की तारीख:</label>
                    <input type="date" id="cattleDate" class="modal-input" style="padding:10px;">
                    <button class="send-btn" style="width:100%; margin-top:5px;" onclick="addCattleBackend()">पशु रिकॉर्ड सुरक्षित करें</button>
                    <div id="cattleList" style="margin-top:15px; font-size:14px; color:#333;"></div>
                </div>

                <div class="info-card">
                    <h3>🥛 दूध का हिसाब (मासिक डायरी)</h3>
                    <div style="display:flex; gap:8px; margin-bottom:10px;">
                        <input type="number" id="milkLitres" placeholder="कुल लीटर दूध" style="width:50%; padding:10px; border-radius:8px; border:1px solid #ccc;">
                        <input type="number" id="milkFat" placeholder="फैट (Fat) जैसे: 4.5" style="width:50%; padding:10px; border-radius:8px; border:1px solid #ccc;">
                    </div>
                    <button class="send-btn" style="width:100%; background-color:#2e7d32;" onclick="addMilkBackend()">हिसाब जोड़ें</button>
                    <div id="milkResult" style="margin-top:15px; font-weight:bold; color:#1b5e20; max-height:200px; overflow-y:auto;"></div>
                </div>
            </div>

            <div id="schemePage" class="page-content">
                <div class="info-card">
                    <h3 id="lbl_sch_title">SCHEME_TITLE_PLACEHOLDER</h3>
                    <p id="lbl_sch_detail" style="line-height:1.6; color:#333;">SCHEME_DETAIL_PLACEHOLDER</p>
                </div>
            </div>

            <div id="adminPage" class="page-content">
                <div class="dashboard-counter">
                    👑 एडमिन डैशबोर्ड | कुल विज़िटर्स (Total Views): VISITOR_COUNT_PLACEHOLDER
                </div>
                <div class="admin-section">
                    <h4>🔄 मंडी रेट अपडेट करें</h4>
                    <input type="text" id="txt_cow" class="modal-input" placeholder="गाय दूध का नया रेट">
                    <input type="text" id="txt_buff" class="modal-input" placeholder="भैंस दूध का नया रेट">
                    <button class="send-btn" style="width:100%; margin-top:5px; background:#e65100;" onclick="updateRatesBackend()">मंडी रेट लाइव बदलें</button>
                </div>
                <div class="admin-section">
                    <h4>🔄 सरकारी योजना बदलें</h4>
                    <input type="text" id="txt_sch_title" class="modal-input" placeholder="योजना का नाम">
                    <textarea id="txt_sch_detail" class="modal-input" placeholder="योजना की पूरी डिटेल लिखें" style="height:80px; font-family:inherit;"></textarea>
                    <button class="send-btn" style="width:100%; margin-top:5px; background:#e65100;" onclick="updateSchemeBackend()">नई योजना लाइव अपलोड करें</button>
                </div>
            </div>

            <div class="nav-bar" id="bottomNav" style="display:none;">
                <button class="nav-item active" id="btn-chat" onclick="switchPage('chatPage', 'btn-chat')">
                    <span class="nav-icon">💬</span><span>एआई चैट</span>
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
                    <span class="nav-icon">👑</span><span>कंट्रोल Panel</span>
                </button>
            </div>

            <div class="modal" id="authModal">
                <div class="modal-content" id="loginBox">
                    <h3>🐄 किसान भाई लॉगिन</h3>
                    <input type="text" id="username" class="modal-input" placeholder="अपना नाम लिखें">
                    <input type="text" id="userphone" class="modal-input" placeholder="10 अंकों का मोबाइल नंबर / एडमिन पासवर्ड">
                    <button class="send-btn" style="width:100%; margin-top:10px;" onclick="sendDemoOTP()">OTP भेजें</button>
                    <button class="auth-btn" style="width:100%; margin-top:5px; background:#eee; color:#333;" onclick="closeAuthModal()">बंद करें</button>
                </div>
                <div class="modal-content" id="otpBox" style="display:none;">
                    <h3>🔐 ओटीपी वेरिफिकेशन</h3>
                    <p style="font-size:13px; color:#ff6d00; font-weight:bold;">कृषि सुरक्षा के लिए डेमो OTP '1234' डालें</p>
                    <input type="number" id="otpInput" class="modal-input" placeholder="4 अंकों का OTP कोड दर्ज करें">
                    <button class="send-btn" style="width:100%; margin-top:10px;" onclick="verifyDemoOTP()">sत्यापित करें</button>
                </div>
            </div>

            <script>
                let currentUserName = "";
                let currentUserPhone = "";
                let base64ImageStr = "";

                // 📌 ऑटो-लॉगिन: अगर यूज़र पहले से लॉगिन है तो बार-बार लॉगिन नहीं मांगेगा
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
                        alert('राम-राम भाई! आप लॉगआउट हो चुके हैं।');
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
                    if(!currentUserName || !currentUserPhone) { alert('कृपया पूरा नाम और सही नंबर भरें!'); return; }
                    
                    if(currentUserPhone === 'Shubham79') {
                        localStorage.setItem("dairy_phone", "Shubham79");
                        localStorage.setItem("dairy_name", "Admin");
                        executeLogin(true);
                        return;
                    }
                    if(currentUserPhone.length < 10) { alert('कृपया सही 10 अंकों का मोबाइल नंबर डालें!'); return; }
                    
                    document.getElementById('loginBox').style.display = 'none';
                    document.getElementById('otpBox').style.display = 'block';
                }

                function verifyDemoOTP() {
                    let otp = document.getElementById('otpInput').value.trim();
                    if(otp === '1234') {
                        localStorage.setItem("dairy_phone", currentUserPhone);
                        localStorage.setItem("dairy_name", currentUserName);
                        executeLogin(false);
                    } else {
                        alert('गलत OTP! कृपया 1234 डालें।');
                    }
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

                // 🎤 100% वर्किंग वॉयस रिकॉग्निशन (बोलकर टाइप करना)
                function startVoiceRecognition() {
                    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    if(!window.SpeechRecognition) { alert("आपका ब्राउज़र बोलकर टाइप करने का समर्थन नहीं करता है।"); return; }
                    
                    const recognition = new SpeechRecognition();
                    recognition.lang = 'hi-IN'; // शुद्ध हिंदी और हिंग्लिश सपोर्ट
                    document.getElementById('micBtn').innerText = "🛑";
                    
                    recognition.onresult = (event) => {
                        const text = event.results[0][0].transcript;
                        document.getElementById('query').value = text;
                    };
                    recognition.onend = () => { document.getElementById('micBtn').innerText = "🎤"; };
                    recognition.start();
                }

                // 📷 फोटो चुनने और उसे एआई के अनुकूल बनाने की क्रिया
                function handleImageUpload(input) {
                    const file = input.files[0];
                    if(!file) return;
                    
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        base64ImageStr = e.target.result.split(',')[1];
                        alert('📷 फोटो सफलतापूर्वक जुड़ गई है! अब अपना सवाल लिखकर या सीधे भेजें दबाएं।');
                    };
                    reader.readAsDataURL(file);
                }

                async function askAI() {
                    let inputField = document.getElementById('query');
                    let q = inputField.value.trim();
                    let chatContainer = document.getElementById('chatContainer');
                    if(!q && !base64ImageStr) return;
                    
                    document.getElementById('globalSpinner').style.display = 'block';
                    
                    // यूजर का मैसेज स्क्रीन पर दिखाएं
                    let userDiv = document.createElement('div');
                    userDiv.className = 'message user-message';
                    userDiv.innerText = q || "📷 फोटो अपलोड की गई";
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
                        base64ImageStr = ""; // रीसेट करें
                        
                        let aiDiv = document.createElement('div');
                        aiDiv.className = 'message ai-message';
                        aiDiv.innerText = data.response || "त्रुटि: जवाब नहीं मिल सका।";
                        chatContainer.appendChild(aiDiv);
                    } catch(e) {
                        alert('सर्वर एरर!');
                    }
                    document.getElementById('globalSpinner').style.display = 'none';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }

                async function loadChatHistory() {
                    let chatContainer = document.getElementById('chatContainer');
                    let res = await fetch('/get_chat?phone=' + currentUserPhone);
                    let data = await res.json();
                    if(data.length > 0) {
                        chatContainer.innerHTML = "";
                        data.forEach(msg => {
                            let div = document.createElement('div');
                            div.className = msg.sender === 'user' ? 'message user-message' : 'message ai-message';
                            div.innerText = msg.message;
                            if(msg.image_url) {
                                let img = document.createElement('img');
                                img.className = 'chat-img';
                                img.src = msg.image_url;
                                div.appendChild(img);
                            }
                            chatContainer.appendChild(div);
                        });
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                    }
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
                    let res = await fetch('/get_cattle?phone=' + currentUserPhone);
                    let data = await res.json();
                    let list = document.getElementById('cattleList');
                    list.innerHTML = "<b>सुरक्षित पशु रिकॉर्ड:</b><br>";
                    data.forEach(c => {
                        list.innerHTML += `• <b>${c.name}</b> (${c.type}) - संभावित तारीख: ${c.date_text}<br>`;
                    });
                }

                async function addMilkBackend() {
                    let lit = parseFloat(document.getElementById('milkLitres').value);
                    let fat = parseFloat(document.getElementById('milkFat').value);
                    if(!lit || !fat) { alert('सही मात्रा भरें!'); return; }
                    
                    let price = fat * 11; // अनुमानित दर
                    let earn = lit * price;
                    
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
                    let res = await fetch('/get_milk?phone=' + currentUserPhone);
                    let data = await res.json();
                    let resDiv = document.getElementById('milkResult');
                    let totalL = 0, totalE = 0;
                    data.forEach(m => { totalL += m.litres; totalE += m.earning; });
                    resDiv.innerHTML = `🥛 कुल दूध: ${totalL.toFixed(1)} लीटर | 💰 कुल जमा राशि: ₹${totalE.toFixed(2)}`;
                }

                async function updateRatesBackend() {
                    let cow = document.getElementById('txt_cow').value.trim();
                    let buff = document.getElementById('txt_buff').value.trim();
                    if(cow) await fetch('/update_setting?key=milk_rate_cow&val=' + encodeURIComponent(cow));
                    if(buff) await fetch('/update_setting?key=milk_rate_buffalo&val=' + encodeURIComponent(buff));
                    alert('मालिक! मंडी रेट पूरी वेबसाइट पर लाइव बदल गया है।');
                }

                async function updateSchemeBackend() {
                    let title = document.getElementById('txt_sch_title').value.trim();
                    let detail = document.getElementById('txt_sch_detail').value.trim();
                    if(title) await fetch('/update_setting?key=scheme_title&val=' + encodeURIComponent(title));
                    if(detail) await fetch('/update_setting?key=scheme_detail&val=' + encodeURIComponent(detail));
                    alert('मालिक! नई योजना लाइव हो चुकी है।');
                }
            </script>
        </body>
    </html>
    """
    # डेटाबेस से लाइव मानों को बदलें
    html_content = html_content.replace("VISITOR_COUNT_PLACEHOLDER", str(v_count))
    html_content = html_content.replace("COW_RATE_PLACEHOLDER", data_dict.get("milk_rate_cow", "₹45"))
    html_content = html_content.replace("BUFF_RATE_PLACEHOLDER", data_dict.get("milk_rate_buffalo", "₹70"))
    html_content = html_content.replace("MUST_RATE_PLACEHOLDER", data_dict.get("feed_rate_mustard", "₹3,000"))
    html_content = html_content.replace("BAG_RATE_PLACEHOLDER", data_dict.get("feed_rate_bag", "₹1,300"))
    html_content = html_content.replace("SCHEME_TITLE_PLACEHOLDER", data_dict.get("scheme_title", "सरकारी योजना"))
    html_content = html_content.replace("SCHEME_DETAIL_PLACEHOLDER", data_dict.get("scheme_detail", "विवरण"))
    
    return html_content

# 🚀 जेमिनी प्रो एडवांस्ड चैट एंड विजन बैकएंड एपीआई
@app.post("/chat_pro")
async def chat_pro(req: Request):
    body = await req.json()
    phone = body.get("phone")
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
    if image_base64:
        # 📷 जेमिनी प्रो को सीधे फोटो भेजने का स्ट्रक्चर
        contents.append(types.Part.from_bytes(data=image_base64.encode(), mime_type="image/jpeg"))

    try:
        res = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.3
            )
        )
        ai_response = res.text
        
        # सुपॉबेस में चैट हिस्ट्री परमानेंट सेव करें
        await query_supabase("chat_history", "POST", {"phone": phone, "sender": "user", "message": query or "📷 फोटो अपलोड"})
        await query_supabase("chat_history", "POST", {"phone": phone, "sender": "ai", "message": ai_response})
        
        return {"response": ai_response}
    except Exception as e:
        return {"response": f"क्षमा करें भाई, समस्या आई: {str(e)}"}

# 📥 डेटा लोड और सेव करने के लिए बाकी डेटाबेस एंडपॉइंट्स
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
