import os
import pandas as pd
from dotenv import load_dotenv
from google import genai 
from google.genai import types
import streamlit as st

#======================
# load menu của quán
menu_df=pd.read_csv("menu.csv")

#=============
#cau hinh chatbot
MODEL_VERSION="gemini-2.5-flash"

#============
# prompt
SYSTEM_INTRO = f"""
Bạn tên là PhoBot, một trợ lý AI có nhiệm vụ hỗ trợ giải đáp thông tin cho khách hàng đến nhà hàng Viet Cuisine.
Các chức năng mà bạn hỗ trợ gồm:
    1. Giới thiệu nhà hàng Viet Cuisine: là một nhà hàng thành lập bởi người Việt, ở địa chỉ 329 Scottmouth, Georgia, USA
    2. Giới thiệu menu của nhà hàng, gồm các món: {', '.join(menu_df['name'].to_list())}.
    3. Hỏi đáp về món ăn trong menu, ví dụ như thành phần món ăn, cách chế biến (dựa trên thông tin trong menu: {menu_df.to_dict(orient='records')})
Ngoài ba chức năng trên, bạn không hỗ trợ chức năng nào khác. Đối với các câu hỏi ngoài chức năng mà bạn hỗ trợ, trả lời bằng 'Tôi đang không hỗ trợ chức năng này. Xin liên hệ nhân viên nhà hàng qua hotline 318-237-3870 để được trợ giúp.'
Hãy có thái độ thân thiện và lịch sự khi nói chuyện với khách hàng, vì khách hàng là thượng đế.
"""


INITIAL_MESS = """
Xin chào!

Tôi là PhoBot - trợ lý trực tuyến của nhà hàng Viet Cuisine.

Tôi có thể hỗ trợ:
- Giới thiệu nhà hàng
- Xem menu món ăn
- Hỏi đáp về món ăn trong menu

Bạn cần tôi giúp gì?
"""
#==============
#ham tao chatbot
def restaurant_chatbot():
    # config trang wweb\
    st.set_page_config(
        page_title="PhoBot - Tro li nha hang VietCuisine",
        layout="wide",
    )
    
    st.title("PhoBot - Viet Cuisine")
    #sidebar
    with st.sidebar:
        st.header(" API ket config")
        api_key=st.text_input(
            "Gemini API key",
            type="password",
            placeholder="Nhap API key cua ban tai day",
        )
        
        st.divider()
        
        st.markdown("""
            ### Chuc nang ho tro
            - Gioi thieu nha hang
            - Xem menu mon an
            - Hoi dap ve mon an trong menu""")
        
    if not api_key:
        st.warning("Vui long nhap gemini api key de bat dau su dung")
        st.stop()

    try:
        client=genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Loi api key: {e}")
        st.stop()
    
    #tao session chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history =[
            {
                "role": "assistant",
                "content": INITIAL_MESS
            }
        ]

    #hthi lich su chat
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    #nhap cau hoi
    prompt = st.chat_input("Nhap cau hoi cua ban tai day...")
    
    if prompt:
        st.session_state.chat_history.append(
            {
                "role":"user",
                "content" :prompt,
            }
        )
        #hthi tin nhan len mhinh
        with st.chat_message("user"):
            st.markdown(prompt)
            
        #toi uu hoa
        if any(word in prompt.lower() for word in ["menu", "thuc don"]):
            chat_response= ""## Duoi day la menu mon an cua nha hang:\n\n"
            for _, row in menu_df.iterrows():
                chat_response+= f'### {row['name']}\n{row['description']}\n'
            else:
                try:
                    response =client.models.generate_content (
                        model=MODEL_VERSION,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INTRO,
                            temperature=0.2,
                            max_output_tokens=1000
                        )
                    )
                    chat_response =response.text
                except Exception as e:
                    st.error(f"Loi khi goi API: {e}")
                    
        #hthi lich su chat
        with st.chat_message("assistant"):
            st.markdown(chat_response)
                    
        #luu lsu chat
        st.session_state.chat_history.append(
            {"role": "assistant", "content": chat_response}
                )
            
            
        


#====================
#chay app
if __name__ =="__main__":
    restaurant_chatbot()