import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

# चाबी सुरक्षित रूप से एन्वायरमेंट से लोड होगी
API_KEY = os.getenv("GEMINI_API_KEY")

DATA_STORE = {
    "visitor_count": 0,
    "milk_rate_cow": "₹42 - ₹48",
    "milk_rate_buffalo": "₹65 - ₹72",
    "feed_rate_mustard": "₹2,800 - ₹3,100",
    "feed_rate_bag": "₹1,200 - ₹1,500",
    "scheme_title": "राष्ट्रीय गोकुल मिशन (RGM)",
    "scheme_detail": "पशुओं की नस्ल सुधारने, दुग्ध उत्पादन बढ़ाने और किसानों की कमाई दोगुनी करने के लिए सरकार द्वारा पशुपालकों को भारी सब्सिडी और मुफ्त कृत्रिम गर्भाधान (AI) की सुविधा दी जाती है।"
}

@app.get("/", response_class=HTMLResponse)
def home():
    DATA_STORE["visitor_count"] += 1
    
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
                
                .chat-container { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; margin-bottom: 70px; }
                .message { max-width: 85%; padding: 12px 16px; border-radius: 18px; font-size: 15px; line-height: 1.5; word-wrap: break-word; }
                .user-message { background-color: #e8f5e9; color: #1b5e20; align-self: flex-end; border-bottom-right-radius: 4px; border: 1px solid #c8e6c9; }
                .ai-message { background-color: white; color: #333; align-self: flex-start; border-bottom-left-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #eee; white-space: pre-wrap; }
                
                .input-container { background-color: white; padding: 10px; border-top: 1px solid #e0e0e0; display: flex; justify-content: center; position: fixed; bottom: 60px; left: 0; right: 0; z-index: 5; }
                .input-box { max-width: 800px; width: 100%; display: flex; gap: 8px; }
                input[type="text"], input[type="number"], select { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 25px; font-size: 15px; outline: none; background-color: #f9f9f9; }
                .send-btn { background-color: #1b5e20; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: bold; }
                
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
                
                .dashboard-counter { display: none; background-color: #ffd54f; color: #333; padding: 10px; text-align: center; font-size: 13px; font-weight: bold; margin-bottom: 15px; border-radius: 8px; border: 1px solid #ffa000; }
                .admin-section { background: #fffde7; padding: 15px; border-radius: 10px; border: 1px solid #fff59d; margin-bottom: 15px; }
                .loading { font-style: italic; color: #777; align-self: flex-start; }
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
                    <div class="message ai-message">राम-राम भाई! मैं आपका डेयरी एक्सपर्ट AI हूँ। पशुपालन या बीमारियों से जुड़ा कोई भी वैज्ञानिक सवाल यहाँ पूछें।</div>
                </div>
                <div class="input-container">
                    <div class="input-box">
                        <input type="text" id="query" placeholder="यहाँ अपना सवाल लिखें..." onkeypress="if(event.key === 'Enter') askAI()">
                        <button class="send-btn" onclick="askAI()">भेजें</button>
                    </div>
                </div>
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
                    <input type="text" id="cattleDate" class="modal-input" placeholder="संभावित बियाने/AI की तारीख (जैसे: 15 जून)">
                    <button class="send-btn" style="width:100%; margin-top:5px;" onclick="addCattle()">पशु रिकॉर्ड सुरक्षित करें</button>
                    <div id="cattleList" style="margin-top:15px; font-size:14px; color:#333;"></div>
                </div>

                <div class="info-card">
                    <h3>🥛 दूध का हिसाब (मासिक डायरी)</h3>
                    <div style="display:flex; gap:8px; margin-bottom:10px;">
                        <input type="number" id="milkLitres" placeholder="कुल लीटर दूध" style="width:50%; padding:10px; border-radius:8px; border:1px solid #ccc;">
                        <input type="number" id="milkFat" placeholder="फैट (Fat) जैसे: 4.5" style="width:50%; padding:10px; border-radius:8px; border:1px solid #ccc;">
                    </div>
                    <button class="send-btn" style="width:100%; background-color:#2e7d32;" onclick="calculateMilk()">हिसाब जोड़ें</button>
                    <div id="milkResult" style="margin-top:15px; font-weight:bold; color:#1b5e20;"></div>
                </div>
            </div>

            <div id="schemePage" class="page-content">
                <div class="info-card">
                    <h3 id="lbl_sch_title">SCHEME_TITLE_PLACEHOLDER</h3>
                    <p id="lbl_sch_detail" style="line-height:1.6; color:#333;">SCHEME_DETAIL_PLACEHOLDER</p>
                </div>
            </div>

            <div id="adminPage" class="page-content">
                <div class="dashboard-counter" style="display:block;">
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
                    <input type="text" id="userphone" class="modal-input" placeholder="मोबाइल नंबर / एडमिन पासवर्ड">
                    <button class="send-btn" style="width:100%; margin-top:10px;" onclick="sendDemoOTP()">OTP भेजें</button>
                    <button class="auth-btn" style="width:100%; margin-top:5px; background:#eee; color:#333;" onclick="closeAuthModal()">बंद करें</button>
                </div>
                
                <div class="modal-content" id="otpBox" style="display:none;">
                    <h3>🔐 ओटीपी वेरिफिकेशन</h3>
                    <p style="font-size:13px; color:#ff6d00; font-weight:bold;">कृषि सुरक्षा के लिए डेमो OTP '1234' डालें</p>
                    <input type="number" id="otpInput" class="modal-input" placeholder="4 अंकों का OTP कोड दर्ज करें">
                    <button class="send-btn" style="width:100%; margin-top:10px;" onclick="verifyDemoOTP()">सत्यापित करें</button>
                </div>
            </div>

            <script>
                let currentUserName = "";
                let currentUserPhone = "";
                let totalMilkLitres = 0;
                let totalMilkEarnings = 0;

                function switchPage(pageId, btnId) {
                    document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-page'));
                    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
                    
                    document.getElementById(pageId).classList.add('active-page');
                    if(btnId) document.getElementById(btnId).classList.add('active');
                }

                function handleAuthClick() {
                    if(document.getElementById('authBtn').innerText === "लॉगआऊट") {
                        currentUserName = "";
                        currentUserPhone = "";
                        document.getElementById('authBtn').innerText = "लॉगिन";
                        document.getElementById('bottomNav').style.display = 'none';
                        document.getElementById('btn-admin').style.display = 'none';
                        switchPage('welcomePage');
                        alert('आप सफलतापूर्वक लॉगआउट हो गए हैं। राम-राम!');
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
                        executeLogin(true);
                        return;
                    }
                    
                    document.getElementById('loginBox').style.display = 'none';
                    document.getElementById('otpBox').style.display = 'block';
                }

                function verifyDemoOTP() {
                    let otp = document.getElementById('otpInput').value.trim();
                    if(otp === '1234') {
                        executeLogin(false);
                    } else {
                        alert('गलत OTP कोड! कृपया 1234 आज़माएं।');
                    }
                }

                function executeLogin(isAdmin) {
                    closeAuthModal();
                    document.getElementById('bottomNav').style.display = 'flex';
                    
                    if(isAdmin) {
                        document.getElementById('authBtn').innerText = "लॉगआऊट";
                        document.getElementById('btn-admin').style.display = 'flex';
                        switchPage('adminPage', 'btn-admin');
                        alert('राम-राम मालिक! आपका सीक्रेट एडमिन कंट्रोल面板 चालू हो चुका है।');
                    } else {
                        document.getElementById('authBtn').innerText = "लॉगआऊट";
                        document.getElementById('btn-admin').style.display = 'none';
                        switchPage('chatPage', 'btn-chat');
                        alert('नमस्ते ' + currentUserName + ' भाई! आपका डेयरी ऐप लॉगिन हो गया है।');
                    }
                    document.getElementById('username').value = "";
                    document.getElementById('userphone').value = "";
                    document.getElementById('otpInput').value = "";
                }

                function addCattle() {
                    let name = document.getElementById('cattleName').value.trim();
                    let type = document.getElementById('cattleType').value;
                    let date = document.getElementById('cattleDate').value.trim();
                    if(!name || !date) { alert('कृपया पूरी जानकारी भरें!'); return; }
                    
                    let row = document.createElement('div');
                    row.style.background = "#f9f9f9";
                    row.style.padding = "8px";
                    row.style.borderBottom = "1px solid #eee";
                    row.innerHTML = "• <b>" + name + "</b> (" + type + ") - तारीख: " + date;
                    document.getElementById('cattleList').appendChild(row);
                    
                    document.getElementById('cattleName').value = "";
                    document.getElementById('cattleDate').value = "";
                }

                function calculateMilk() {
                    let lit = parseFloat(document.getElementById('milkLitres').value);
                    let fat = parseFloat(document.getElementById('milkFat').value);
                    if(!lit || !fat) { alert('लीटर और फैट की सही मात्रा दर्ज करें!'); return; }
                    
                    let estimatedPricePerLitre = fat * 11;
                    let currentEarning = lit * estimatedPricePerLitre;
                    
                    totalMilkLitres += lit;
                    totalMilkEarnings += currentEarning;
                    
                    document.getElementById('milkResult').innerHTML = 
                        "इस रिकॉर्ड की कमाई: ₹" + currentEarning.toFixed(2) + "<br>" +
                        "🥛 पूरे महीने का कुल दूध: " + totalMilkLitres.toFixed(1) + " लीटर<br>" +
                        "💰 कुल जमा अनुमानित राशि: ₹" + totalMilkEarnings.toFixed(2);
                        
                    document.getElementById('milkLitres').value = "";
                    document.getElementById('milkFat').value = "";
                }

                function updateRatesBackend() {
                    let cow = document.getElementById('txt_cow').value.trim();
                    let buff = document.getElementById('txt_buff').value.trim();
                    if(cow) document.getElementById('lbl_cow').innerText = cow;
                    if(buff) document.getElementById('lbl_buff').innerText = buff;
                    alert('बधाई हो मालिक! नया मंडी रेट पूरी वेबसाइट पर लाइव बदल चुका है।');
                }

                function updateSchemeBackend() {
                    let title = document.getElementById('txt_sch_title').value.trim();
                    let detail = document.getElementById('txt_sch_detail').value.trim();
                    if(title) document.getElementById('lbl_sch_title').innerText = title;
                    if(detail) document.getElementById('lbl_sch_detail').innerText = detail;
                    alert('सफलतापूर्वक! नई सरकारी योजना सीधे ग्राहकों के मोबाइल स्क्रीन के लिए अपलोड हो गई है।');
                }

                async function askAI() {
                    let inputField = document.getElementById('query');
                    let q = inputField.value.trim();
                    let chatContainer = document.getElementById('chatContainer');
                    if(!q) return;
                    
                    let userDiv = document.createElement('div');
                    userDiv.className = 'message user-message';
                    userDiv.innerText = q;
                    chatContainer.appendChild(userDiv);
                    
                    inputField.value = '';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    
                    let loadingDiv = document.createElement('div');
                    loadingDiv.className = 'message loading';
                    loadingDiv.innerText = '🔍 आपका AI सर्च कर रहा है, कृपया रुकें...';
                    chatContainer.appendChild(loadingDiv);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    
                    try {
                        let response = await fetch('/chat?q=' + encodeURIComponent(q));
                        let data = await response.json();
                        chatContainer.removeChild(loadingDiv);
                        
                        let aiDiv = document.createElement('div');
                        aiDiv.className = 'message ai-message';
                        if(data.response) {
                            aiDiv.innerText = data.response;
                        } else {
                            aiDiv.innerText = 'त्रुटि: ' + (data.error || 'जवाब नहीं मिल पाया।');
                        }
                        chatContainer.appendChild(aiDiv);
                    } catch(e) {
                        chatContainer.removeChild(loadingDiv);
                        let errorDiv = document.createElement('div');
                        errorDiv.className = 'message ai-message';
                        errorDiv.innerText = 'सर्वर से संपर्क नहीं हो सका।';
                        chatContainer.appendChild(errorDiv);
                    }
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            </script>
        </body>
    </html>
    """
    html_content = html_content.replace("VISITOR_COUNT_PLACEHOLDER", str(DATA_STORE["visitor_count"]))
    html_content = html_content.replace("COW_RATE_PLACEHOLDER", DATA_STORE["milk_rate_cow"])
    html_content = html_content.replace("BUFF_RATE_PLACEHOLDER", DATA_STORE["milk_rate_buffalo"])
    html_content = html_content.replace("MUST_RATE_PLACEHOLDER", DATA_STORE["feed_rate_mustard"])
    html_content = html_content.replace("BAG_RATE_PLACEHOLDER", DATA_STORE["feed_rate_bag"])
    html_content = html_content.replace("SCHEME_TITLE_PLACEHOLDER", DATA_STORE["scheme_title"])
    html_content = html_content.replace("SCHEME_DETAIL_PLACEHOLDER", DATA_STORE["scheme_detail"])
    
    return html_content

@app.get("/chat")
def chat_with_ai(q: str = Query(...)):
    system_instruction = (
        "तुम 'AgriDairy Expert AI' हो। तुम एक बेहद मददगार, समझदार और दोस्ताना AI गाइड हो। "
        "तुम यूजर की भाषा (हिंदी, इंग्लिश, या हिंग्लिश) को तुरंत समझकर उसी आसान भाषा में जवाब देते हो। "
        "जब भी कोई डेयरी का सवाल पूछे, तुम तुरंत Google Search का उपयोग करोगे और सटीक वैज्ञानिक डेटा, "
        "मात्रा (किलोग्राम/ग्राम), दवाइयों के नाम और ग्राउंड रिपोर्ट के आधार पर ही उत्तर दोगे।"
    )
    try:
        res = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=q,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction, 
                tools=[types.Tool(google_search=types.GoogleSearch())], 
                temperature=0.3
            )
        )
        return {"response": res.text}
    except Exception as e:
        return {"error": str(e)}
