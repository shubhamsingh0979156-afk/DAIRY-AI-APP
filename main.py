import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

# आपकी लाइव API Key
API_KEY = "AIzaSyDozCATJgbrcC6gfmRVXh3twglLl8SwHa8"
client = genai.Client(api_key=API_KEY)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AgriDairy Expert AI</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { box-sizing: border-box; }
                body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f7f5; margin: 0; display: flex; flex-direction: column; height: 100vh; }
                
                /* हेडर स्टाइल */
                .header { background-color: #1b5e20; color: white; padding: 15px; text-align: center; font-size: 20px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                
                /* चैट एरिया जहाँ मैसेज दिखेंगे */
                .chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; max-width: 800px; width: 100%; margin: 0 auto; }
                
                /* मैसेज बबल्स की स्टाइल */
                .message { max-width: 85%; padding: 12px 16px; border-radius: 18px; font-size: 15px; line-height: 1.5; word-wrap: break-word; }
                
                /* यूजर का मैसेज (Gemini Style) */
                .user-message { background-color: #e8f5e9; color: #1b5e20; align-self: flex-end; border-bottom-right-radius: 4px; border: 1px solid #c8e6c9; }
                
                /* AI का जवाब (Gemini Style) */
                .ai-message { background-color: white; color: #333; align-self: flex-start; border-bottom-left-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #eee; white-space: pre-wrap; }
                
                /* बॉटम इनपुट बॉक्स एरिया */
                .input-container { background-color: white; padding: 15px; border-top: 1px solid #e0e0e0; display: flex; justify-content: center; position: sticky; bottom: 0; }
                .input-box { max-width: 800px; width: 100%; display: flex; gap: 10px; align-items: center; }
                
                input[type="text"] { flex: 1; padding: 14px; border: 1px solid #ccc; border-radius: 25px; font-size: 15px; outline: none; background-color: #f9f9f9; transition: all 0.3s; }
                input[type="text"]:focus { border-color: #1b5e20; background-color: white; box-shadow: 0 0 5px rgba(27,94,32,0.2); }
                
                button { background-color: #1b5e20; color: white; border: none; padding: 14px 24px; border-radius: 25px; cursor: pointer; font-size: 15px; font-weight: bold; transition: background 0.2s; }
                button:hover { background-color: #113d14; }
                
                /* लोडिंग एनीमेशन */
                .loading { font-style: italic; color: #777; align-self: flex-start; background: transparent; padding: 5px 10px; }
            </style>
        </head>
        <body>
            <div class="header">🐄 AgriDairy Expert AI</div>
            
            <div class="chat-container" id="chatContainer">
                <div class="message ai-message">नमस्ते भाई! मैं आपका डेयरी एक्सपर्ट AI हूँ। पशुपालन, गाय-भैंस के दूध की मात्रा बढ़ाने या उनके स्वास्थ्य से जुड़ा कोई भी सवाल यहाँ नीचे चैट बॉक्स में पूछें।</div>
            </div>
            
            <div class="input-container">
                <div class="input-box">
                    <input type="text" id="query" placeholder="यहाँ अपना सवाल लिखें..." onkeypress="if(event.key === 'Enter') askAI()">
                    <button onclick="askAI()">भेजें</button>
                </div>
            </div>

            <script>
                async function askAI() {
                    let inputField = document.getElementById('query');
                    let q = inputField.value.trim();
                    let chatContainer = document.getElementById('chatContainer');
                    if(!q) return;
                    
                    // 1. यूजर का मैसेज स्क्रीन पर जोड़ें
                    let userDiv = document.createElement('div');
                    userDiv.className = 'message user-message';
                    userDiv.innerText = q;
                    chatContainer.appendChild(userDiv);
                    
                    // इनपुट बॉक्स खाली करें और नीचे स्क्रॉल करें
                    inputField.value = '';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    
                    // 2. लोडिंग मैसेज दिखाएं
                    let loadingDiv = document.createElement('div');
                    loadingDiv.className = 'message loading';
                    loadingDiv.innerText = '🔍 आपका AI सर्च कर रहा है, कृपया रुकें...';
                    chatContainer.appendChild(loadingDiv);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    
                    try {
                        let response = await fetch('/chat?q=' + encodeURIComponent(q));
                        let data = await response.json();
                        
                        // लोडिंग हटाएं
                        chatContainer.removeChild(loadingDiv);
                        
                        // 3. AI का जवाब स्क्रीन पर जोड़ें
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
                    
                    // हर मैसेज के बाद अपने आप नीचे स्क्रॉल करें
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            </script>
        </body>
    </html>
    """

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
