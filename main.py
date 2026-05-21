import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

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
                body { font-family: Arial, sans-serif; background-color: #f7f9fc; padding: 15px; margin: 0; display: flex; justify-content: center; }
                .container { max-width: 450px; width: 100%; background: white; padding: 25px; border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05); margin-top: 20px; box-sizing: border-box; }
                h2 { color: #1e4620; margin-top: 0; font-size: 24px; text-align: center; }
                p { color: #555; font-size: 14px; line-height: 1.5; text-align: center; }
                input[type="text"] { width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #ced4da; border-radius: 8px; font-size: 15px; box-sizing: border-box; }
                button { background-color: #2e7d32; color: white; width: 100%; padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; }
                #result { margin-top: 20px; text-align: left; background: #f1f3f4; padding: 15px; border-radius: 8px; white-space: pre-wrap; font-size: 14px; line-height: 1.6; color: #333; border-left: 4px solid #2e7d32; display: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🐄 AgriDairy Expert AI</h2>
                <p>डेयरी फार्मिंग का कोई भी सवाल यहाँ अपनी भाषा में पूछें:</p>
                <input type="text" id="query" placeholder="जैसे: गाय के दूध की मात्रा कैसे बढ़ाएं?">
                <button onclick="askAI()">जवाब खोजें</button>
                <div id="result"></div>
            </div>

            <script>
                async function askAI() {
                    let q = document.getElementById('query').value;
                    let resultDiv = document.getElementById('result');
                    if(!q) { alert('कृपया अपना सवाल लिखें!'); return; }
                    resultDiv.style.display = 'block';
                    resultDiv.innerText = '🔍 आपका एक्सपर्ट AI सर्च कर रहा है, कृपया कुछ सेकंड रुकें...';
                    
                    try {
                        let response = await fetch('/chat?q=' + encodeURIComponent(q));
                        let data = await response.json();
                        if(data.response) {
                            resultDiv.innerText = data.response;
                        } else {
                            resultDiv.innerText = 'त्रुटि: ' + (data.error || 'जवाब नहीं मिल पाया।');
                        }
                    } catch(e) {
                        resultDiv.innerText = 'सर्वर से संपर्क नहीं हो सका।';
                    }
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
