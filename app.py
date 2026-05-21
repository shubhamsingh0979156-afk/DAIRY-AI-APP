import streamlit as str
import requests

# आपकी वेबसाइट का सुंदर नाम
str.set_page_config(page_title="AgriDairy Expert AI", page_icon="🐄")
str.title("🐄 AgriDairy Expert AI")
str.write("डेयरी फार्मिंग से जुड़ा कोई भी सवाल यहाँ पूछें। हमारा AI सीधे गूगल सर्च से सटीक डेटा निकालकर जवाब देगा।")

# सवाल इनपुट करने का बॉक्स
user_query = str.text_input("अपना सवाल यहाँ लिखें (जैसे: गाय के दूध की मात्रा कैसे बढ़ाएं?):")

if str.button("जवाब खोजें"):
    if user_query:
        str.info("AI जवाब तैयार कर रहा है, कृपया कुछ सेकंड रुकें...")
        # आपके रेंडर सर्वर से कनेक्ट करना
        backend_url = f"https://dairyiaapp.onrender.com/chat?q={user_query}"
        try:
            response = requests.get(backend_url)
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    str.success("🎯 सटीक जवाब:")
                    str.write(data["response"])
                elif "error" in data:
                    str.error(f"सर्वर एरर: {data['error']}")
            else:
                str.error("सर्वर से संपर्क नहीं हो पाया। कृपया रेंडर पर अपना सर्वर चेक करें।")
        except Exception as e:
            str.error(f"कोई गड़बड़ हुई: {e}")
    else:
        str.warning("कृपया पहले कोई सवाल टाइप करें!")
