import streamlit as st
import re
import pandas as pd
import streamlit.components.v1 as stc
import requests
from streamlit_option_menu import option_menu
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from PIL import Image
import datetime

API_KEY = "a36bb8ff5a7878f0ea6173dab14c7291"

@st.cache(allow_output_mutation=True)
def load_data(data):
    df = pd.read_csv(data, nrows=3000,na_filter=False)
    return df 

@st.cache(allow_output_mutation=True)
def getCategory(category):
    k = [""]
    for item in category:
        if not item in k:
            k.append(item)
    return k

@st.cache(allow_output_mutation=True)
def getState(state):
    k = [""]
    for item in state:
        if not item in k:
            k.append(item)
    return k

# Vectorize and cosine similarity matrix
def vectorize_text_to_cosine_similarity(data):
    count_vector = CountVectorizer()
    cv_matrix = count_vector.fit_transform(data)
    #get cosine similarity
    cosine_similarity_matrix = cosine_similarity(cv_matrix)
    return cosine_similarity_matrix

@st.cache(allow_output_mutation=True)
def getRecommend(search_term, state, rate1, rate2, df, cosine_similarity_matrix):
    #fulfill the condition of category and rating first then only filter
    df["Rating"] = pd.to_numeric(df["Rating"])
    df = df[(df.State == state) & (df.Category.str.contains(search_term,flags=re.IGNORECASE)) & (df.Rating >= rate1) & (df.Rating <= rate2)]
    #index of places
    place_indices = pd.Series(df.index, index = df['Category'])
    idx = place_indices[search_term]
    #cosine matrix
    sim_score = list(enumerate(cosine_similarity_matrix[idx]))
    #sim_score = sorted(sim_score, key=lambda x: x[1], reverse=True)
    selected_place_indices = [i[0] for i in sim_score[1:]]
    #get dataframe 
    result_df = df.iloc[selected_place_indices]
    recommend = result_df[['State', 'Place_Name', 'Rating', 'Description', 'Website', 'Location_Link', 'Food_Recommendation_Nearby', 'Accommodation_Nearby', 'Address', 'Phone_Number',	'Category',	'Picture_Link']]
    final_recommend = recommend
    return final_recommend

#state, place_name, rating, description, website, location_link, food_recommendation_nearby, accommodation_nearby, address, phone_number, category, picture_link
htmlResult = '''
<div style="width:200%;height:50%;margin:1px;padding:5px;position:relative;border-bottom-right-radius: 30px;
; background-color: #a8f0c6;
  border-left: 5px solid #00cc777; font-family: sans serif; font-size: 16px">

<p style="color:black;"><style="font:sans serif"><span style="color:#292928;">&#127760 State: </span>{}</p>
<p style="color:black;"><span style="color:black;">&#127961 Place Name: </span>{}</p>
<p style="color:black;"><span style="color:black;">&#127775 Rating: </span>{}</p>
<p style="color:black;"><span style="color:black;">&#128462 Description: </span>{}</p>
<p style="color:black;"><span style="color:black;">🔗 </span><a href="{}", target="_blank" rel="noreferrer noopener">Website</a></p>
<p style="color:black;"><span style="color:black;">🔗 </span><a href="{}", target="_blank" rel="noreferrer noopener">Location Link</a></p>
<p style="color:black;"><span style="color:black;">🔗 </span><a href="{}", target="_blank" rel="noreferrer noopener">Food Recommendation Nearby</a></p>
<p style="color:black;"><span style="color:black;">🔗 </span><a href="{}", target="_blank" rel="noreferrer noopener">Accommodation Nearby</a></p>
<p style="color:black;"><span style="color:black;">&#127968 Address: </span>{}</p>
<p style="color:black;"><span style="color:black;">&#128222 Phone Number: </span>{}</p>
<p style="color:black;"><span style="color:black;">Category: </span>{}</p>
<p style="color:black;"><span style="color:black;"></span><a href="{}", target ="_blank" rel="noreferrer noopener"><img src="{}" alt="Place Image " width="250" height="250"></img></a></p>
</div>
'''

st.set_page_config(
    page_title="Places Recommender",
    page_icon="logo1.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

#SIDEBAR
st.title("Places Recommender")
with st.sidebar:

    #LOGO
    image = Image.open('logo1.png')
    st.image(image, width=160)

    #MENU
    choose = option_menu("Menu", ["Home", "Recommendation", "About", "Help Centre"],
        icons=['house', 'search', 'info-circle', 'question-circle'],
        menu_icon="app-indicator", default_index=0,
        styles={
    "container": {"padding": "10px", "background-color": "#ffffff"},
    "icon": {"color": "green", "font-size": "18px"},
    "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#a8f0c6"},
    "nav-link-selected": {"background-color": "#36b56b"},
        })
    
    #CALENDAR
    st.subheader("Calendar")
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    start_date = st.date_input('Today', today)

    #WEATHER
    def convert_to_celcius(temperature_in_kelvin):
        return temperature_in_kelvin -273.15
    
    def find_current_weather(city):
        base_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        weather_data = requests.get(base_url).json()
        try:
            general = weather_data['weather'][0]['main']
            icon_id = weather_data['weather'][0]['icon']
            temperature = round(convert_to_celcius (weather_data['main']['temp']))
            icon = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        except KeyError:
            st.error("City Not Found")
            st.stop()
        return general, temperature, icon
    
    def main():
        st.subheader("Weather")
        city = st.text_input("Enter City").lower()
        if st.button("Find"):
            general, temperature, icon = find_current_weather(city)
            col_1, col_2 = st.columns(2)
            with col_1:
                st.metric(label="Temperature", value=f"{temperature}°C")
            with col_2:
                st.write(general)
                st.image(icon)

    if __name__ == '__main__':
        main()

df = load_data("Malaysia Tourist Attraction.csv")
df.columns = [c.replace(' ', '_') for c in df.columns]

#HOMEPAGE
if choose == "Home":
    st.markdown("---")
    st.header("Home")
    image = Image.open('homepage1.png')
    st.image(image)
    st.header("")
    st.markdown(""" <style> .font1{
        font-size: 60px; font-family: 'Sans Serif'; color: #00000;}
        </style> """, unsafe_allow_html=True)
    st.markdown('<h1> <p class="font1", style="text-align: center;"><b><br>Welcome!<br></b></h1></p>',unsafe_allow_html=True)
    st.markdown(""" <style> .font2{
        font-size: 40px; font: 'Sans Serif'; color: #141414;}
        </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font2", style="text-align: center;"><br>This system will help you complete your travel plans to <b>Malaysia</b>.<br><br></p>',unsafe_allow_html=True)
    st.header("")
    image = Image.open('homepage2.png')
    st.image(image)
    st.header("")
    st.markdown(""" <style> .font3{ 
        font-size: 40px; font-style:'Sans Serif'; color: #00000;}
        </style>""", unsafe_allow_html=True)
    st.markdown('<p class="font3", style="text-align: center;"><br>More about <b>Malaysia</b><br><br></p>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
            st.video("https://youtu.be/WP3NsJVU-78")
            st.markdown(""" <style> .font4{
            font-size: 15px; font4: 'Sans Serif'; color: #00000;}
            </style> """, unsafe_allow_html=True)
            st.markdown('<p class="font", style="text-align: center;">Credit: <a href="https://youtu.be/WP3NsJVU-78">Peter Tong on Youtube</a></p>',unsafe_allow_html=True)
    with col4:
            st.video("https://youtu.be/BVVyMzXAjMc")
            st.markdown(""" <style> .font5{
            font-size: 15px; font5: 'Sans Serif'; color: #00000;}
            </style> """, unsafe_allow_html=True)
            st.markdown('<p class="font", style="text-align: center;">Credit: <a href="https://youtu.be/BVVyMzXAjMc">Malaysia Truly Asia on Youtube</a></p>',unsafe_allow_html=True)
        
    st.markdown("---")
    st.caption("Copyright (C) 2022 Farah Nurshaziela")


#RECOMMEND PAGE
elif choose == "Recommendation":
    st.markdown("---")
    st.header("Places Recommendation")
    cosine_similarity_matrix = vectorize_text_to_cosine_similarity(df['Category'])
    num_of_record = all
    state= st.selectbox("State",getState(df["State"]))
    #search_term = st.text_input("Search")
    search_term = st.selectbox("Category",getCategory(df["Category"]))
    rating = ["4.0 - 5.0", "3.0 - 4.0", "2.0 - 3.0", "1.0 - 2.0", "0.0 - 1.0"]
    rate = st.radio("Rating (from Google Review)", rating)
    rate1 = rate2 = 0
    if(rate == "4.0 - 5.0"):
        rate1 = 4.0
        rate2 = 5.0
    elif rate == "3.0 - 4.0":
        rate1 = 3.0
        rate2 = 4.0
    elif rate == "2.0 - 3.0":
        rate1 = 2.0
        rate2 = 3.0
    elif rate == "1.0 - 2.0":
        rate1 = 1.0
        rate2 = 2.0
    elif rate == "0.0 - 1.0":
        rate1 = 0.0
        rate2 = 1.0
    if(st.button("Search")):
     if state == "":
            st.error('Please select state', icon="🚨")
     if not search_term == "":
            try:
                results = getRecommend(search_term, state, rate1, rate2, df, cosine_similarity_matrix)
                print("Recommend Results:", len(results))
                if len(results) == all:
                    results = "Not Found"
                    st.warning(results)
                else:
                    st.subheader("Results")
                    if(len(results) == all):
                        print("Results:")
                        results = results.sample(n=num_of_record,replace=False)
                        print(results)
                    for row in results.iterrows():
                        state  = row[1][0]
                        place_name = row[1][1]
                        rating = row[1][2]
                        description = row[1][3]
                        website = row[1][4]
                        location_link = row[1][5]
                        food_recommendation_nearby = row[1][6]
                        accommodation_nearby = row[1][7]
                        address = row[1][8]
                        phone_number = row[1][9]
                        category = row[1][10]
                        picture_link = row[1][11]
                        stc.html(htmlResult.format(state, place_name, rating, description, website, location_link, food_recommendation_nearby, accommodation_nearby, address, phone_number, category, picture_link, picture_link), height=670 if not picture_link == "" else 450)
            except:
                results = "Not Found"
                st.warning(results)
     else:
            st.error('Please enter search term', icon="🚨")
    st.markdown("---")
    st.caption("Copyright (C) 2022 Farah Nurshaziela")


#ABOUT PAGE
elif choose == "About":
    st.markdown("---")
    st.header("About")
    tab1, tab2 = st.tabs(["System", "Developer"])
    with tab1:
        st.image("about2.png")
        st.markdown(""" <style> .font6{
            font-size: 20px; font-style:'Sans Serif'; color:#000000;}
            </style>""", unsafe_allow_html=True)
        st.markdown('<p class="font6", style="text-align: right-aligned;"><br>This system is built in order to help local and foreign tourist in finding a suitable places to visit here in Malaysia in accordance to their preferences.</br><p>', unsafe_allow_html=True)
    with tab2:
        st.image("about1.png")
        st.markdown(""" <style> .font7{ 
        font-size: 20px; font-style:'Sans Serif'; color: #00000;}
        </style>""", unsafe_allow_html=True)
        st.markdown('<p class="font7", style="text-align: right-aligned;"><br>Farah Nurshaziela is a final year student in University of Technology Mara, Perlis, taking Bachelor in Information Technology.</br><br>This system "Web-based Application for Places Recommender using Machine Learning" is her Final Year Project title.</br><br>This project is supervised by Dr. Ruzita Ahmad and co-supervised by Prof. Madya Ts. Dr. Shukor Sanim bin Mohd Fauzi.</br><br> For more information click: <a href="https://fnurshaziela.carrd.co/">https://fnurshaziela.carrd.co/</a></br></p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Copyright (C) Farah Nurshaziela 2022")

#HELP CENTRE PAGE
else:
    st.markdown("---")
    st.header("Help Centre")
    tab3, tab4 = st.tabs(["How To", "Contact Us"])
    with tab3:
        st.subheader("Demonstration on How To Use the System")
        st.video("System Demo.mp4")
    with tab4:
        st.subheader("Feedback Form")
        feedback_form = """
        <form action = "https://formsubmit.co/fnurshaziela@gmail.com" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="Your name" required>
            <input type="email" name="email" placeholder="Your email" required>
            <textarea name="message" placeholder="Your feedback here"></textarea>
            <button type="submit">Send</button>
        </form>
        """

        st.markdown(feedback_form, unsafe_allow_html=True)

        def local_css(style):
            with open(style) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        local_css("style/style.css")

    st.markdown("---")
    st.caption("Copyright (C) Farah Nurshaziela 2022")
