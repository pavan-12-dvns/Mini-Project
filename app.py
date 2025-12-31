import streamlit as st
import pandas as pd
import math
import plotly.express as px

st.set_page_config(page_title="Smart Wellness Assistant", layout="wide")

# ------------------------ FOOD DATABASE ------------------------
FOOD_DB = {
    "Oats": {"cal": 389, "protein": 17, "carbs": 66, "fat": 7, "fiber": 10.6},
    "Milk": {"cal": 60, "protein": 3.2, "carbs": 5, "fat": 3.5, "fiber": 0},
    "Egg": {"cal": 155, "protein": 13, "carbs": 1.1, "fat": 11, "fiber": 0},
    "Banana": {"cal": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "fiber": 2.6},
    "Rice": {"cal": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4},
    "Roti": {"cal": 120, "protein": 3.0, "carbs": 20, "fat": 3.0, "fiber": 3.9},
    "Chicken Breast": {"cal": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0},
    "Paneer": {"cal": 265, "protein": 18, "carbs": 6, "fat": 20, "fiber": 0},
    "Almonds": {"cal": 579, "protein": 21, "carbs": 22, "fat": 50, "fiber": 12.5},
    "Broccoli": {"cal": 34, "protein": 2.8, "carbs": 6.6, "fat": 0.4, "fiber": 2.6},
    "Dal": {"cal": 116, "protein": 9, "carbs": 20, "fat": 0.4, "fiber": 7.9},
    "Curd": {"cal": 98, "protein": 11, "carbs": 3.4, "fat": 4.3, "fiber": 0}
}

# ------------------------ Functions ------------------------
def calc_macros(food, grams):
    f = FOOD_DB[food]
    factor = grams / 100
    return {
        "cal": f["cal"] * factor,
        "protein": f["protein"] * factor,
        "carbs": f["carbs"] * factor,
        "fat": f["fat"] * factor,
        "fiber": f["fiber"] * factor
    }

def bmr(weight, height, age, gender):
    return (10*weight + 6.25*height - 5*age + (5 if gender=="Male" else -161))

def activity_mult(level):
    return {"Sedentary":1.2, "Light":1.375, "Moderate":1.55, "Active":1.725, "Very Active":1.9}[level]

def calc_targets(user, goal):
    base = user["bmr"] * activity_mult(user["activity"])
    cal = base * (0.85 if goal=="Lose Weight" else 1.15 if goal=="Gain Weight" else 1)
    protein = 1.6 * user["weight"]
    fat = 0.25 * cal / 9
    carb = (cal - (protein*4 + fat*9)) / 4
    fiber = (cal / 1000) * 14
    return round(cal), round(protein), round(carb), round(fat), round(fiber)

# ------------------------ Sidebar ------------------------
st.sidebar.title("🏥 Navigation")
page = st.sidebar.radio("Go to", ["Home","Enter Details","Food Calculator","Daily Summary","Diet Plan","Workout Recommendation","About"])

# ------------------------ HOME ------------------------
if page == "Home":
    st.title("💚 Smart Wellness Recommendation Assistant")
    st.write("All-in-one Nutrition + Diet + Workout AI Web App for Python mini-projects!")

# ------------------------ ENTER DETAILS ------------------------
elif page == "Enter Details":
    st.title("🧑‍⚕️ Personal Info")
    with st.form("form"):
        name = st.text_input("Name")
        age = st.number_input("Age",10,100,20)
        gender = st.selectbox("Gender",["Male","Female"])
        weight = st.number_input("Weight (kg)",25.0,200.0,60.0)
        height = st.number_input("Height (cm)",120.0,230.0,170.0)
        activity = st.selectbox("Activity",["Sedentary","Light","Moderate","Active","Very Active"])
        goal = st.selectbox("Goal",["Maintain","Lose Weight","Gain Weight"])
        save = st.form_submit_button("Save")
        if save:
            u = {"name":name,"age":age,"gender":gender,"weight":weight,"height":height,"activity":activity}
            u["bmr"]=bmr(weight,height,age,gender)
            u["cal"],u["protein"],u["carbs"],u["fat"],u["fiber"]=calc_targets(u,goal)
            u["goal"]=goal
            st.session_state.user = u
            st.success("✔ User details saved!")

# ------------------------ FOOD CALCULATOR ------------------------
elif page == "Food Calculator":
    st.title("🍏 Food Macro Calculator")

    if "intake" not in st.session_state: st.session_state.intake=[]

    food = st.selectbox("Select food", list(FOOD_DB.keys()))
    grams = st.number_input("Enter grams",1,800,100)

    # Show macros LIVE
    m = calc_macros(food, grams)
    st.info(f"📊 Macros for {grams}g {food}:")
    st.write(f"Calories ➤ {m['cal']:.1f} kcal")
    st.write(f"Protein ➤ {m['protein']:.1f} g")
    st.write(f"Carbs ➤ {m['carbs']:.1f} g")
    st.write(f"Fat ➤ {m['fat']:.1f} g")
    st.write(f"Fiber ➤ {m['fiber']:.1f} g")

    # Save only if user chooses
    if st.button("➕ Add to Daily Intake (Optional)"):
        st.session_state.intake.append({"food":food,"grams":grams, **m})
        st.success("Saved!")

    # Show table immediately
    if st.session_state.intake:
        st.subheader("🧾 Today's Saved Items")
        st.dataframe(pd.DataFrame(st.session_state.intake))

# ------------------------ DAILY SUMMARY ------------------------
elif page == "Daily Summary":
    st.title("📊 Daily Nutrition Summary")
    if "intake" not in st.session_state or not st.session_state.intake:
        st.warning("No food added.")
    else:
        df = pd.DataFrame(st.session_state.intake)
        totals = df.sum()
        st.metric("Calories",f"{totals['cal']:.0f} kcal")
        st.metric("Protein",f"{totals['protein']:.1f} g")
        st.metric("Carbs",f"{totals['carbs']:.1f} g")
        st.metric("Fat",f"{totals['fat']:.1f} g")
        fig = px.pie(values=[totals["protein"],totals["carbs"],totals["fat"]],names=["Protein","Carbs","Fat"])
        st.plotly_chart(fig)

# ------------------------ DIET PLAN ------------------------
elif page == "Diet Plan":
    st.title("🍽 Custom Diet Plan")
    if "user" not in st.session_state:
        st.warning("Enter details first!")
    else:
        u = st.session_state.user
        st.write(f"🎯 Daily Target ➤ {u['cal']} kcal")
        st.write(f"Protein: {u['protein']} g | Carbs: {u['carbs']} g | Fat: {u['fat']} g | Fiber: {u['fiber']} g")

        MEALS = {"🥣 Breakfast":0.25,"🍛 Lunch":0.35,"🍎 Snacks":0.10,"🍽 Dinner":0.30}
        for meal,pct in MEALS.items():
            st.subheader(meal)
            st.write(f"Calories ➤ {int(u['cal']*pct)} kcal | Protein ➤ {int(u['protein']*pct)}g | Carbs ➤ {int(u['carbs']*pct)}g | Fat ➤ {int(u['fat']*pct)}g | Fiber ➤ {int(u['fiber']*pct)}g")
            st.write("Suggested Foods:")
            st.write("• Oats + Milk + Egg" if meal=="🥣 Breakfast" else 
                     "• Rice + Chicken / Paneer + Dal" if meal=="🍛 Lunch" else
                     "• Fruit + Nuts" if meal=="🍎 Snacks" else
                     "• Roti + Dal + Veggies")

# ------------------------ WORKOUT RECOMMENDATION ------------------------
elif page == "Workout Recommendation":
    st.title("🏋️ Gym Workout Recommendation")

    level = st.selectbox("Experience Level",["Beginner","Intermediate","Advanced"])
    goal = st.selectbox("Goal",["Muscle Gain","Fat Loss"])

    st.markdown("### 📅 Recommended Split")

    if level=="Beginner":
        st.write("➡ 3 Days — Full Body Split")
        plan = {
            "Day 1": ["Squat – 3×10","Pushups – 3×12","Lat Pulldown – 3×12"],
            "Day 2": ["Leg Press – 3×12","Bench Press – 3×10","Seated Row – 3×12"],
            "Day 3": ["Lunges – 3×12","Shoulder Press – 3×10","Plank – 3×30s"]
        }
    elif level=="Intermediate":
        st.write("➡ 4 Days — Upper / Lower Split")
        plan = {
            "Day 1 (Upper)": ["Bench Press – 4×8","Pullups – 3×8","Shoulder Press – 3×10"],
            "Day 2 (Lower)": ["Squats – 4×8","Leg Curl – 3×10","Calf Raise – 3×12"],
            "Day 3 (Upper)": ["Incline Press – 4×8","Rows – 4×8","Dips – 3×10"],
            "Day 4 (Lower)": ["Deadlift – 3×5","Leg Press – 3×12","Abs – 3×15"]
        }
    else:
        st.write("➡ 6 Days — Push / Pull / Legs")
        plan = {
            "Push": ["Bench Press – 5×5","Shoulder Press – 4×8","Tricep Dip – 4×10"],
            "Pull": ["Deadlift – 5×3","Barbell Row – 4×8","Curl – 3×10"],
            "Legs": ["Squat – 5×5","Leg Press – 4×10","Calf Raise – 4×12"]
        }

    for day,ex in plan.items():
        st.subheader(day)
        for e in ex: st.write("• "+e)

# ------------------------ ABOUT ------------------------
elif page == "About":
    st.title("ℹ About Project")
    st.write("Python Smart Wellness Assistant — Nutrition + Macro + Workout")

