import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

# आपकी एक्टिव जेमिनी API Key
API_KEY = "AIzaSyDozCATJgbrcC6gfmRVXh3twglLl8SwHa8"
client = genai.Client(api_key=API_KEY)

# यूज़र्स की कुल गिनती
VISITOR_COUNT = 0

@app.get("/", response_class=HTMLResponse)
def home():
    global VISITOR_COUNT
    VISITOR_COUNT += 1  # हर विज़िट पर गिनती बढ़ेगी
    
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>AgriDairy Expert AI Pro</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f7f5; margin: 0; padding-bottom: 60px; height: 100vh; display: flex; flex-direction: column; }}
                
                .header {{ background-color: #1b5e20; color: white; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; font-size: 18px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); z-index: 10; }}
                .login-btn {{ background-color: #ffff; color: #1b5e20; border: none; padding: 6px 14px; border-radius: 20px; font-size: 14px; cursor: pointer; font-weight: bold; }}
                
                /* विज्ञापन स्पेस */
                .ad-placeholder {{ background-color: #f1f3f4; border: 1px dashed #bbb; color: #777; text-align: center; padding: 10px; font-size: 12px; margin: 5px auto; max-width: 800px; width: 95%; border-radius: 5px; }}
                
                .page-content {{ flex: 1; display: none; overflow-y: auto; padding: 15px; max-width: 800px; width: 100%; margin: 0 auto; }}
                .active-page {{ display: flex; flex-direction: column; }}
                
                .chat-container {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; margin-bottom: 70px; }}
                .message {{ max-width: 85%; padding: 12px 16px; border-radius: 18px; font-size: 15px; line-height: 1.5; word-wrap: break-word; }}
                .user-message {{ background-color: #e8f5e9; color: #1b5e20; align-self: flex-end; border-bottom-right-radius: 4px; border: 1px solid #c8e6c9; }}
                .ai-message {{ background-color: white; color: #333; align-self: flex-start; border-bottom-left-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #eee; white-space: pre-wrap; }}
                
                .input-container {{ background-color: white; padding: 10px; border-top: 1px solid #e0e0e0; display: flex; justify-content: center; position: fixed; bottom: 60px; left: 0; right: 0; z-index: 5; }}
                .input-box {{ max-width: 800px; width: 100%; display: flex; gap: 8px; }}
                input[type="text"] {{ flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 25px; font-size: 15px; outline: none; background-color: #f9f9f9; }}
                .send-btn {{ background-color: #1b5e20; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: bold; }}
                
                /* यह काउंटर शुरू में छुपा रहेगा */
                .dashboard-counter {{ display: none; background-color: #ffd54f; color: #333; padding: 8px; text-align: center; font-size: 13px; font-weight: bold; position: fixed; bottom: 60px; left: 0; right: 0; z-index: 20; border-top: 1px solid #ffa000; box-shadow: 0 -2px 5px rgba(0,0,0,0.1); }}
                
                .info-card {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 4px solid #1b5e20; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; background: white; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }}
                th {{ background-color: #e8f5e9; color: #1b5e20; }}
                
                .nav-bar {{ background-color: white; border-top: 1px solid #e0e0e0; position: fixed; bottom: 0; left: 0; right: 0; height: 60px; display: flex; justify-content: space-around; align-items: center; z-index: 10; }}
                .nav-item {{ background: none; border: none; color: #666; display: flex; flex-direction: column; align-items: center; font-size: 12px; cursor: pointer; font-weight: 500; }}
                .nav-item.active {{ color: #1b5e20; font-weight: bold; }}
                .nav-icon {{ font-size: 18px; margin-bottom: 2px; }}
                
                .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; z-index: 100; }}
                .modal-content {{ background: white; padding: 25px; border-radius: 15px; width: 90%; max-width: 350px; text-align: center; }}
                .modal-input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; }}
                
                .loading {{ font-style: italic; color: #777; align-self: flex-start; }}
            </style>
        </head>
        <body>

            <div class="header">
                <div>🐄 AgriDairy Expert</div>
                <button class="login-btn" id="loginBtn" onclick="openLogin()">लॉगिन</button>
            </div>
            
            <div class="ad-placeholder" id="topAd">Google Ads यहाँ दिखाई देंगे (यूज़र को बिना डिस्टर्ब किए)</div>

            <div id="chatPage" class="page-content active-page">
                <div class="chat-container" id="chatContainer">
                    <div class="message ai-message">राम-राम भाई! मैं आपका डेयरी एक्सपर्ट AI हूँ। पशुपालन, दूध बढ़ाने या पशुओं की बीमारी से जुड़ा कोई भी सवाल यहाँ नीचे पूछें।</div>
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
                        <tr><th>वस्तु (Item)</th><th>अनुमानित रेट (Price)</th></tr>
                        <tr><td>गाय का दूध (प्रति लीटर - 4.0 Fat)</td><td>₹42 - ₹48</td></tr>
                        <tr><td>भैंस का दूध (प्रति लीटर - 6.5 Fat)</td><td>₹65 - ₹72</td></tr>
                        <tr><td>सरसों खली (प्रति क्विंटल)</td><td>₹2,800 - ₹3,100</td></tr>
                        <tr><td>पशु आहार/फीड (50KG बैग)</td><td>₹1,200 - ₹1,500</td></tr>
                    </table>
                </div>
            </div>

            <div id="schemePage" class="page-content">
                <div class="info-card">
                    <h3>📜 डेयरी सरकारी योजनाएं एवं लोन सब्सिडी</h3>
                    <h4>1. राष्ट्रीय गोकुल मिशन (RGM)</h4>
                    <p>पशुओं की नस्ल सुधारने और दूध उत्पादन बढ़ाने के लिए सरकार द्वारा भारी सब्सिडी दी जाती है।</p>
                </div>
            </div>

            <div class="dashboard-counter" id="ownerDashboard">
                👑 एडमिन डैशबोर्ड | कुल विज़िटर्स (Total Views): {VISITOR_COUNT}
            </div>

            <div class="nav-bar">
                <button class="nav-item active" id="btn-chat" onclick="switchPage('chatPage', 'btn-chat')">
                    <span class="nav-icon">💬</span><span>एआई चैट</span>
                </button>
                <button class="nav-item" id="btn-rate" onclick="switchPage('ratePage', 'btn-rate')">
                    <span class="nav-icon">📈</span><span>मंडी रेट</span>
                </button>
                <button class="nav-item" id="btn-scheme" onclick="switchPage('schemePage', 'btn-scheme')">
                    <span class="nav-icon">📜</span><span>योजनाएं</span>
                </button>
            </div>

            <div class="modal" id="loginModal">
                <div class="modal-content">
                    <h3>🐄 पशुपालक लॉगिन</h3>
                    <p style="font-size:12px; color:#666;">मालिक लॉगिन के लिए मोबाइल नंबर की जगह सीक्रेट पासवर्ड डालें</p>
                    <input type="text" id="username" class="modal-input" placeholder="अपना नाम लिखें">
                    <input type="password" id="userphone" class="modal-input" placeholder="मोबाइल नंबर या पासवर्ड">
                    <button class="send-btn" style="width:100%; margin-top:10px;" onclick="submitLogin()">Sign In</button>
                    <button class="login-btn" style="width:100%; margin-top:5px; background:#eee; color:#333;" onclick="closeLogin()">बंद करें</button>
                </div>
            </div>

            <script>
                function switchPage(pageId, btnId) {{
                    document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-page'));
                    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
                    
                    document.getElementById(pageId).classList.add('active-page');
                    document.getElementById(btnId).classList.add('active');
                }}

                function openLogin() {{ document.getElementById('loginModal').style.display = 'flex'; }}
                function closeLogin() {{ document.getElementById('loginModal').style.display = 'none'; }}
                
                function submitLogin() {{
                    let name = document.getElementById('username').value.trim();
                    let pass = document.getElementById('userphone').value.trim();
                    if(!name) {{ alert('कृपया नाम लिखें!'); return; }}
                    
                    if(pass === 'Shubham79') {{
                        document.getElementById('loginBtn').innerText = "👑 " + name + " (Owner)";
                        document.getElementById('ownerDashboard').style.display = 'block';
                        alert('राम-राम मालिक! आपका सीक्रेट डैशबोर्ड एक्टिव हो गया है।');
                    }} else {{
                        document.getElementById('loginBtn').innerText = "👤 " + name;
                        document.getElementById('ownerDashboard').style.display = 'none';
                    }}
                    closeLogin();
                }}

                async function askAI() {{
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
                    
                    try {{
                        let response = await fetch('/chat?q=' + encodeURIComponent(q));
                        let data = await response.json();
                        
                        chatContainer.removeChild(loadingDiv);
                        
                        let aiDiv = document.createElement('div');
                        aiDiv.className = 'message ai-message';
                        if(data.response) {{
                            aiDiv.innerText = data.response;
                        }} else {{
                            aiDiv.innerText = 'त्रुटि: ' + (data.error || 'जवाब नहीं मिल पाया।');
                        }}
                        chatContainer.appendChild(aiDiv);
                    } catch(e) {{
                        chatContainer.removeChild(loadingDiv);
                        let errorDiv = document.createElement('div');
                        errorDiv.className = 'message ai-message';
                        errorDiv.innerText = 'सर्वर से संपर्क नहीं हो सका।';
                        chatContainer.appendChild(errorDiv);
                    }}
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }}
            </script>
        </body>
    </html>
    """

@app.get("/chat")
def chat_with_ai(q: str = Query(...)):
    system_instruction = (
        "तुम 'AgriDairy Expert AI' हो। तुम एक बेहद मददगार, समझदार and दोस्ताना AI गाइड हो। "
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
