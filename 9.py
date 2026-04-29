import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
from datetime import date
import gspread   # ✅ 要加這行

import uuid
from datetime import datetime
#終端機輸入streamlit run c:/Users/Jinzer/Desktop/python/問卷收集/9.py
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False

if "page" not in st.session_state:
    st.session_state["page"] = 1
st.title("📊 發展可規模化之台灣胰臟癌高風險族群 臨床試驗/研究受試者問卷")
from google.oauth2.service_account import Credentials
def init_gsheet():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    #自己內網的話
    # creds = ServiceAccountCredentials.from_json_keyfile_name(
    # r"c:\Users\Jinzer\Desktop\dogwood-cinema-494201-u6-e5739d95639f.json", scope
    # )

    # client = gspread.authorize(creds)
    #公開網路的話
    #Streamlit → Google Sheets（雲端Excel）
    creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
    )
    client = gspread.authorize(creds)

    sheet = client.open("問卷資料").sheet1
    return sheet
def save_to_gsheet(data):

    sheet = init_gsheet()

    # 👉 如果你有標題列（建議一定要有）
    headers = sheet.row_values(1)

    row = []
    for h in headers:
        row.append(data.get(h, ""))

    sheet.append_row(row)

# ======================
# 問卷題目
# ======================
#st.radio     選項 ≤ 5~7 個
#st.selectbox 選項很多（> 7 個）
# ======================
# 初始化 page
# ======================
# ======================
# 下一頁 / 上一頁控制
# ======================
def next_page():
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1
# =========================
# 📌 第 1 頁
# =========================
def safe_list(x):
    return x if isinstance(x, list) else []

def clean_data(data):
    choices3 = data.get("choices3") or []
    if not isinstance(choices3, list):
        choices3 = []

    choices3 = [x for x in choices3 if x != "其他"]

    return {
        "symptoms": choices3,
        "no_symptom": bool(data.get("no_disease3")),
        "other_symptom": data.get("other_sy")
    }



BASIC_SCHEMA = [
    "pid",
    "age",
    "gender",
    "height",
    "weight",
    "weight_1y",
    "blood_type",
    "dob",
    "email",
]
MEDICAL_SCHEMA = [
    "final_choices",
    "cancer_type",
    "cancer_year",
    "cancer_month",
    "cancer_age",
    "acute_age",
    "acute_treat_times",
    "chronic_age",
    "chronic_treat_times",
    "diabetes_type",
    "diabetes_age",
    "diabetes_treatment",
    "exam",
    "MRI_treatment",
    "answer1",
    "answer2",
    "gene",
    "probiotics",
    "antibiotics",
    "colonoscopy",
]
FAMILY_SCHEMA = [
    "family_rows",
    "other_family_rows",
]
LIFESTYLE_SCHEMA = [
    "smoke",
    "smokes",
    "smokes_years",
    "quit_year",
    "quit_month",
    "quit_age",
    "other_smoke",
    "other_smoke_type",
    "smokes_other",
    "drink1",
    "drink2",
    "drink_freq",
    "max_drink",
    "max_drink_type",
    "drink4",
]
EXPORT_SCHEMA = (
    BASIC_SCHEMA +
    MEDICAL_SCHEMA +
    FAMILY_SCHEMA +
    LIFESTYLE_SCHEMA
)


for k in EXPORT_SCHEMA:
    st.session_state.setdefault(k, None)


if st.session_state.page == 1:
    st.header("📌 1. 基本資料")
    st.subheader("請填寫個人基本資料")
    st.divider()
    with st.form("survey"):
        # ===== 個案編號 =====
        pid = st.text_input("個案編號", placeholder="請輸入個案編號")
        # ===== 基本資料 =====
        age = st.number_input("年齡", min_value=1, max_value=120,value=None,placeholder="請輸入年齡")

        gender = st.selectbox("性別", ["男", "女"],index=None)

        height = st.number_input("身高 (公分)", min_value=50, max_value=230,value=None,placeholder="請輸入身高")

        weight = st.number_input("體重 (公斤)", min_value=1, max_value=230,value=None,placeholder="請輸入體重")

        weight_1y = st.number_input("一年前體重 (公斤)", min_value=1, max_value=230,value=None,placeholder="請輸入一年前體重")

        blood_type = st.selectbox("血型", ["A", "B", "AB", "O","Rh","不清楚"],index=None,placeholder="請選擇血型")

        dob = st.date_input("出生年月日",value=None, min_value=date(1900, 1, 1),max_value=date.today())

        email = st.text_input("E-mail", placeholder="請輸入 email")
        # if dob:
        #     today = date.today()
        #     agecount = today.year - dob.year - (
        #         (today.month, today.day) < (dob.month, dob.day)
        #     )
        #     st.write(f"年齡: {agecount}")
        #     st.session_state["agecount"] = agecount
        submitted = st.form_submit_button("下一頁 ➡")

        if submitted:
            missing = [v for v in [pid, age, gender, height, weight,weight_1y, blood_type, dob, email] if not v]
            if missing:
                st.error("⚠️ 仍有空格尚未填寫")
            else:
                # st.session_state["pid"] = pid  # 🔥 強制寫入
                # st.session_state["age"] = age  # 🔥 強制寫入
                # st.session_state["gender"] = gender  # 🔥 強制寫入
                # st.session_state["height"] = height  # 🔥 強制寫入
                # st.session_state["weight"] = weight  # 🔥 強制寫入
                # st.session_state["weight_1y"] = weight_1y  # 🔥 強制寫入
                # st.session_state["blood_type"] = blood_type  # 🔥 強制寫入
                # st.session_state["dob"] = dob  # 🔥 強制寫入
                # st.session_state["email"] = email  # 🔥 強制寫入
                st.session_state.page = 2
                st.rerun()

        # if submitted:
        #     if pid == "":
        #         st.warning("⚠️ 請輸入個案編號")
        #     elif email == "":
        #         st.error("❌ 請輸入 Email")
        #     elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        #         st.error("❌ Email 格式不正確")
        #     elif age == 0 or age is None:
        #         st.error("❌ 請輸入年齡")
        #     elif dob is None:
        #         st.error("請填寫出生年月日")
        #     else:
        #         st.session_state["gender"] = gender  # 🔥 強制寫入
        #         st.session_state.page = 2
        #         st.rerun()
        st.divider()
# =========================
# PAGE 2
# =========================


elif st.session_state.page == 2:
    st.header("📌 2. 既往病史")
    st.subheader("請填寫既往病史")
    st.divider()


    import streamlit as st

    def sync_no_disease():
        if st.session_state["no_disease"]:
            st.session_state["choices"] = []

    def sync_choices():
        if st.session_state["choices"]:
            st.session_state["no_disease"] = False


    choices = st.multiselect(
        "您是否曾患有下列慢性疾病（請在適當項目前打勾）",
        ["高血壓", "心臟病", "癌症", "急性胰臟炎", "慢性胰臟炎", "糖尿病"],
        key="choices",
        on_change=sync_choices
    )

    no_disease = st.checkbox(
        "以上皆無",
        key="no_disease",
        on_change=sync_no_disease
    )

    final_choices = [] if st.session_state.get("no_disease") else st.session_state.get("choices", [])
    # =========================
    # =========================
    # 🅰️A選項 → 額外輸入
    # =========================
    if "癌症" in choices:
        with st.expander("🧬 癌症資料"):
            cancer_type = st.text_input("請輸入曾患有的癌症", key="cancer_type")
            
            col1, col2 = st.columns(2)
            with col1:
                cancer_year = st.selectbox("罹癌___年",[""] + list(range(1, 91)),index=0,key="cancer_year")
            with col2:
                cancer_month = st.selectbox("罹癌___月",[""] + list(range(1, 13)),index=0,key="cancer_month")
            if cancer_year == "" or cancer_month == "":
                st.warning("請完整填寫患癌時間")
                st.stop()
            cancer_age = st.number_input("請輸入患癌年齡", key="cancer_age", min_value=10, max_value=120,value=None,placeholder="請輸入患癌年齡多少年了")
    if "急性胰臟炎" in choices:
        with st.expander("🧪 急性胰臟炎"):
            acute_age = st.number_input("請輸入發生急性胰臟炎的年齡", key="acute_age", min_value=10, max_value=120,value=None,placeholder="請輸入發生急性胰臟炎的年齡")
            acute_treat_times = st.number_input("請輸入治療次數", key="acute_treat_times", min_value=0, max_value=120,value=None,placeholder="請輸入治療次數")
    if "慢性胰臟炎" in choices:
        with st.expander("🧪 慢性胰臟炎資料"):
            chronic_age =  st.number_input("請輸入發生急性胰臟炎的年齡", key="chronic_age", min_value=10, max_value=120,value=None,placeholder="請輸入發生急性胰臟炎的年齡")
            chronic_treat_times =st.number_input("請輸入治療次數", key="chronic_treat_times", min_value=0, max_value=120,value=None,placeholder="請輸入治療次數")
    if "糖尿病" in choices:
        with st.expander("🩸 糖尿病資料"):
            diabetes_type = st.selectbox("請選擇糖尿病類型",["第一型", "第二型", "不知道"],index=None,key="diabetes_type")
            diabetes_age = st.number_input("請輸入診斷出糖尿病時的年齡", key="diabetes_age", min_value=0, max_value=120,value=None,placeholder="請輸入診斷出糖尿病時的年齡")
            diabetes_treatment  = st.selectbox('治療方式',["無", "斷食", "口服藥物","注射胰島素","不知道"],index=None,key="diabetes_treatment")
            st.subheader("若有藥物治療，請後續使用E-mail或Line方式提供藥物名稱")
    st.divider()
    exam = st.selectbox("過去一年內是否做過內視鏡超音波或MRI檢查?",
        ["是", "否"],index=None,key="exam")
    
    if exam == "是":
        MRI_treatment = st.selectbox("檢查方式",["MRI", "內視鏡超音波"],
            index=None,key="MRI_treatment")

    answer1 = st.selectbox(
        "胰臟癌症家族病史?",["無", "有"],
        key="answer1",index=None)
    

    # =========================
    # 胰臟癌家族病史
    # =========================
    if answer1 == "有":
        st.session_state["answer1"] = None

        st.markdown("### 👨‍👩‍👧‍👦 家族病史填寫")
        if "family_count" not in st.session_state:
            st.session_state.family_count = 1
        MAX_FAMILY = 3
        col_add1, col_del1 = st.columns(2)

        with col_add1:
            if st.button("➕ 新增一筆家族資料", key="add_family"):
                if st.session_state.family_count < MAX_FAMILY:
                    st.session_state.family_count += 1
                    st.rerun()
                else:
                    st.warning("最多只能輸入 3 筆家族資料")

        with col_del1:
            if st.button("➖ 刪除一筆家族資料", key="del_family"):
                if st.session_state.family_count > 1:
                    st.session_state.family_count -= 1
                    st.rerun()
        for i in range(st.session_state.family_count):
            st.markdown(f"### 👨‍👩‍👧‍👦 第 {i+1} 筆")

            st.number_input(
                "幾歲罹癌",
                key=f"page3_cancer_age_{i}",
                min_value=10,
                max_value=120,
                value=None,
                placeholder="請輸入幾歲罹癌"
            )

            st.text_input(
                "稱謂（父親/母親/兄弟）",
                key=f"page3_relation_{i}"
            )

            choices1 = st.selectbox(
                "與之關係",
                ["一等親", "二等親", "其他"],
                key=f"page3_relation_type_{i}"
            )

            if choices1 == "其他":
                st.text_input(
                    "請填寫與之關係",
                    key=f"page3_relation_other_{i}"
                )
    answer2 = st.selectbox("其他家族病史?",["無", "有"],key="answer2",index=None)
    # =========================
    # 其他家族病史
    # =========================
    if answer2 == "有":
        st.markdown("### 👨‍👩‍👧‍👦 其他家族病史填寫")

        if "other_count" not in st.session_state:
            st.session_state.other_count = 1
        MAX_FAMILY = 3
        col_add2, col_del2 = st.columns(2)
        with col_add2:
            if st.button("➕ 新增一筆家族資料", key="add_other"):
                st.session_state.other_count += 1
                st.rerun()

        with col_del2:
            if st.button("➖ 刪除一筆家族資料", key="del_other"):
                if st.session_state.other_count > 1:
                    st.session_state.other_count -= 1
                    st.rerun()
        for i in range(st.session_state.other_count):
                st.markdown(f"### 👨‍👩‍👧‍👦 第 {i+1} 筆")

                st.number_input(
                    "幾歲罹癌",
                    key=f"other_cancer_age_{i}",
                    min_value=10,
                    max_value=120,
                    value=None,
                    placeholder="請輸入幾歲罹癌"
                )
                st.text_input(
                    "稱謂（父親/母親/兄弟）",
                    key=f"other_relation_{i}"
                )
                choices2= st.selectbox(
                    "與之關係",
                    ["一等親", "二等親", "其他"],
                    key=f"other_relation_type_{i}"
                )

                if choices2 == "其他":
                    st.text_input(
                        "請填寫與之關係",
                        key=f"other_relation_other_{i}"
                    )

    gene = st.selectbox("本人或家族是否有接受過基因檢測", ["是", "否"],key="gene",index=None)
    probiotics = st.selectbox("過去兩周內是否有服用益生菌?", ["是", "否"],key="probiotics",index=None)
    antibiotics = st.selectbox("過去一個月內是否服用過抗生素?", ["是", "否"],key="antibiotics",index=None)
    colonoscopy = st.selectbox("過去一個月內是否做過大腸鏡檢查?", ["是", "否"],key="colonoscopy",index=None)


    # =========================
    # 同步：選症狀 → 取消以上皆無
    # =========================
    def sync_choices3():
        if st.session_state.get("choices3"):
            st.session_state["no_disease3"] = False

    # =========================
    # 同步：勾以上皆無 → 清空症狀
    # =========================
    def clear_symptoms3():
        if st.session_state.get("no_disease3"):
            st.session_state["choices3"] = []
            st.session_state["other_sy"] = ""
    # =========================
    # multiselect（症狀）
    # =========================
    choices3 = st.multiselect(
        "過去一年內是否出現以下症狀",
        [
            "腹脹","腹痛","上腹痛","背痛","急性糖尿病","體重下降","食量降低","食慾不振",
            "眼白/皮膚呈現黃色","血尿","排便習慣改變","皮膚搔癢感","疲勞或虛弱感",
            "噁心或嘔吐感","嘔吐","其他"
        ],
        key="choices3",
        on_change=sync_choices3
    )

    no_disease3 = st.checkbox(
        "以上皆無（症狀）",
        key="no_disease3",
        on_change=clear_symptoms3
    )

    # ========================
    # 其他症狀（只在選其他時出現）
    # =========================
    other_sy = None
    if "其他" in st.session_state.get("choices3", []):
        other_sy = st.text_input(
            "請填寫其他症狀",
            key="other_sy"
        )

    # =========================
    # 乾淨資料整理（給分析用）
    # =========================
    clean_choices3 = st.session_state.get("choices3", [])

    # 互斥規則：以上皆無
    if st.session_state.get("no_disease3"):
        clean_choices3 = []

    # 去掉 "其他" 本身（分析用）
    clean_choices3 = [x for x in clean_choices3 if x != "其他"]

    # =========================
    # final output（研究用）
    # =========================
    final_data = {
        "symptoms": clean_choices3,
        "no_symptom": st.session_state.get("no_disease3", False),
        "other_symptom": other_sy
    }

    st.session_state["final_choices3"] = final_data
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ 上一頁"):
            st.session_state.page = 1
            st.rerun()

    with col2:
        if st.button("下一頁 ➡"):
            errors = []
            # ======================
            # 1️⃣ 基本必填檢查
            # ======================
            if not st.session_state.get("no_disease") and not st.session_state.get("choices"):
                errors.append("請至少選擇一項疾病，或勾選「以上皆無」")

            if st.session_state.get("exam") is None:
                errors.append("請填寫是否做過內視鏡或MRI")

            if st.session_state.get("answer1") is None:
                errors.append("請填寫胰臟癌家族病史")

            if st.session_state.get("answer2") is None:
                errors.append("請填寫其他家族病史")

            if st.session_state.get("gene") is None:
                errors.append("請填寫基因檢測")

            if st.session_state.get("probiotics") is None:
                errors.append("請填寫是否服用益生菌")

            if st.session_state.get("antibiotics") is None:
                errors.append("請填寫是否服用抗生素")

            if st.session_state.get("colonoscopy") is None:
                errors.append("請填寫是否做過大腸鏡")
            # ======================
            # 2️⃣ 家族病史（胰臟癌）
            # ======================
            if st.session_state.get("answer1") == "有":
                for i in range(st.session_state.get("family_count", 1)):

                    age12 = st.session_state.get(f"page3_cancer_age_{i}")
                    relation = st.session_state.get(f"page3_relation_{i}")
                    rel_type = st.session_state.get(f"page3_relation_type_{i}", [])
                    other12 = st.session_state.get(f"page3_relation_other_{i}")

                    if age12 is None:
                        errors.append(f"胰臟癌家族病史 第{i+1}筆：請填寫幾歲罹癌")

                    if not relation:
                        errors.append(f"胰臟癌家族病史 第{i+1}筆：請填寫稱謂")

                    if not rel_type:
                        errors.append(f"胰臟癌家族病史 第{i+1}筆：請選擇與之關係")

                    if "其他" in rel_type and not other12:
                        errors.append(f"胰臟癌家族病史 第{i+1}筆：請填寫其他關係")

            # ======================
            # 3️⃣ 其他家族病史
            # ======================
            if st.session_state.get("answer2") == "有":
                for i in range(st.session_state.get("other_count", 1)):

                    age13 = st.session_state.get(f"other_cancer_age_{i}")
                    relation = st.session_state.get(f"other_relation_{i}")
                    rel_type = st.session_state.get(f"other_relation_type_{i}", [])
                    other13 = st.session_state.get(f"other_relation_other_{i}")

                    if age13 is None:
                        errors.append(f"其他家族病史 第{i+1}筆：請填寫幾歲罹癌")

                    if not relation:
                        errors.append(f"其他家族病史 第{i+1}筆：請填寫稱謂")

                    if not rel_type:
                        errors.append(f"其他家族病史 第{i+1}筆：請選擇與之關係")

                    if "其他" in rel_type and not other13:
                        errors.append(f"其他家族病史 第{i+1}筆：請填寫其他關係")

            # ======================
            # 2️⃣ 顯示錯誤 or 換頁
            # ======================
            if errors:
                for e in errors:
                    st.error(f"⚠️ {e}")
                st.stop()
            else:
                # st.session_state["final_choices"] = st.session_state.get("final_choices", [])
                # st.session_state["cancer_type"] = st.session_state.get("cancer_type")
                # st.session_state["cancer_year"] = st.session_state.get("cancer_year")
                # st.session_state["cancer_month"] = st.session_state.get("cancer_month")
                # st.session_state["cancer_age"] = st.session_state.get("cancer_age")
                # st.session_state["acute_age"] = st.session_state.get("acute_age")
                # st.session_state["acute_treat_times"] = st.session_state.get("acute_treat_times")
                # st.session_state["chronic_age"] = st.session_state.get("chronic_age")
                # st.session_state["chronic_treat_times"] = st.session_state.get("chronic_treat_times")
                # st.session_state["diabetes_type"] = st.session_state.get("diabetes_type")
                # st.session_state["diabetes_age"] = st.session_state.get("diabetes_age")
                # st.session_state["diabetes_treatment"] = st.session_state.get("diabetes_treatment")
                # st.session_state["exam"] = st.session_state.get("exam")
                # st.session_state["MRI_treatment"] = st.session_state.get("MRI_treatment")
                # st.session_state["answer1"] = st.session_state.get("answer1")
                rows = []
                for i in range(3):
                    rows.append({
                        "family_id": i+1,
                        "age": st.session_state.get(f"page3_cancer_age_{i}"),
                        "relation": st.session_state.get(f"page3_relation_{i}"),
                        "type": st.session_state.get(f"page3_relation_type_{i}"),
                        "other": st.session_state.get(f"page3_relation_other_{i}")
                    })
                st.session_state["family_rows"] = rows
                other_rows = []
                for i in range(3):  # 如果你也要固定3筆
                    other_rows.append({
                        "family_id": i + 1,
                        "age": st.session_state.get(f"other_cancer_age_{i}"),
                        "relation": st.session_state.get(f"other_relation_{i}"),
                        "type": st.session_state.get(f"other_relation_type_{i}"),
                        "other": st.session_state.get(f"other_relation_other_{i}")
                    })

                # 🔥 強制寫入 session_state
                st.session_state["other_family_rows"] = other_rows


                st.session_state.page = 3
                st.rerun()



elif st.session_state.page == 3:
    st.header("📌 3. 生活習慣")
    st.subheader("請填寫生活習慣")
    st.divider()
    st.markdown("#### 🚬 抽菸習慣")
    # =========================
    # 吸菸
    # =========================
    smoke = st.selectbox(
        "請問您過去是否有吸菸?",
        ["從未吸菸","偶爾吸(不是每天)","每天吸(幾乎)","已經戒菸"],
        key="smoke",index=None
    )
    # choices2 = st.session_state.get("choices2") 
    # if not choices2:
    #     choices2 = []

    # elif isinstance(choices2, str):
    #     choices2 = [choices2]

    if smoke == "每天吸(幾乎)":
        avg_smoke = st.number_input("平均每天幾支菸", key="smokes", min_value=1, max_value=120,value=None,placeholder="請輸入平均每天幾支菸")
        smoke_age = st.number_input("菸齡", key="smokes_years", min_value=10, max_value=120,value=None,placeholder="請輸入抽菸多少年了")
        if avg_smoke == "" :
            st.warning("請完整填寫平均每天幾支菸")
            st.stop()
        if smoke_age == "" :
            st.warning("請完整填寫菸齡")
            st.stop()



    if smoke=="已經戒菸" :
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("戒菸___年", list(range(1, 91)), key="quit_year",index=None)
        with col2:
            st.selectbox("戒菸___月", list(range(1, 13)), key="quit_month",index=None)
        st.number_input("幾歲時戒菸", key="quit_age", min_value=10, max_value=120,value=None,placeholder="請輸入戒菸時的年齡")
    # =========================
    # 其他菸品
    # =========================
    
    other_smoke = st.selectbox("是否使用其他菸品",["否", "是"], key="other_smoke",index=None)
    selected = []  # 🔥 一定先初始化（重點）

    if other_smoke == "是":
        st.multiselect(
            "其他菸品",
            ["電子菸", "菸斗", "雪茄","加熱菸", "其他"],
            key="other_smoke_type",
        )
        # ⚠️ 一定要從 session_state 讀值
        selected = st.session_state.get("other_smoke_type") or []

    if "其他" in selected:
        st.text_input(
            "請描述使用的其他菸品",
            key="smokes_other",
            placeholder="請輸入菸品")
    st.divider()

    # =========================
    # 飲酒（建議：獨立block但仍在同form）
    # =========================
    st.markdown("#### 🍺 飲酒習慣")
    st.markdown("""
    一個標準杯的飲料含有大約14克酒精  
    相當於       
                   
    - 🍺 啤酒（約 350 ml, 5%）：一罐約 350 毫升、5% 酒精濃度的啤酒  
    - 🍷 紅酒（約 150 ml, 12%）：一杯約 150 毫升、12% 酒精濃度的葡萄酒  
    - 🥃 蒸餾酒（約 45 ml, 40%）：一份約 1.5 盎司（45 毫升）的烈酒（高粱、威士忌、清酒等）
    """)
    drinking_levels = [
        "每天", "一周5-6天", "一周3-4天", "一周2天", "一周1天",
        "一個月2-3天", "一個月1天", "一年3-11天", "1年1-2天"]
    drink1 = st.selectbox("2.請問您過去一年喝酒情況?", 
        drinking_levels + ["未曾飲酒"],
        index=None,key="drink1")
    if drink1 in drinking_levels:
        st.session_state["drink_flag"] = 1
        alcohol_type = st.selectbox("過去一年主要的飲用酒類",["啤酒", "紅酒", "蒸餾酒"],index=None,key="alcohol_type")
        drink2= st.selectbox("2-1.請問您過去一年喝的酒精含量(單位:杯)",
            ["25杯以上","19-24杯","16-18杯","12-15杯","9-11杯","7-8杯","5-6杯","3-4杯","2","1"],
            key="drink2",index=None)
        gender = st.session_state.get("gender", "請選擇")
        if gender == "男":
            drink_question = "2-2.男生: 請問您過去一年中是否有2小時內喝完 等量的5罐啤酒 / 5杯紅酒 或 蒸餾酒頻率?"

        elif gender == "女":
            drink_question = "2-2.女生: 請問您過去一年中是否有2小時內喝完 等量的4罐啤酒 / 4杯紅酒 或 蒸餾酒頻率?"
        else:
            st.warning("請先選擇性別")
            st.stop()
        drink_freq = st.selectbox(drink_question,drinking_levels+["沒有"],index=None,key="drink_freq")    
        max_drink = st.selectbox("2-3請問一生中，單日(24小時內)最大酒精量為何?(單位:杯)",
                             ["36杯以上", "24-35杯", "18-23杯", "12-17杯", "8-11杯", "5-7杯", "4杯", "3杯","2杯","1杯"],
                key="max_drink",index=None)
        # ===== 最大飲酒量 =====
        max_drink_type = st.selectbox("單日最大的飲用酒類",["啤酒", "紅酒", "蒸餾酒"],index=None,key="max_drink_type")
        drink4 = st.selectbox("是否已戒酒?",["否", "是"],index=None,key="drink4")
        if drink4 == "是":
            col3, col4 = st.columns(2)
            with col3:
                quit_year = st.selectbox("戒酒___年",[""] + list(range(1, 91)),index=0,key="quit_year")
            with col4:
                quit_month = st.selectbox("戒酒___月",[""] + list(range(1, 13)),index=0,key="quit_month")
                # st.selectbox("戒酒___月", list(range(1, 13)), key="quit_month",index=None)
            if quit_year == "" or quit_month == "":
                st.warning("請完整填寫戒酒時間")
                st.stop()

        # =========================
        # 最終送出（唯一出口）
        # =========================

    # st.button("✅ 完成問卷", on_click=lambda: st.session_state.update({"page": 4}))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ 上一頁"):
            st.session_state.page = st.session_state.page - 1
            st.rerun()
    with col2:
        if st.button("✅ 完成問卷") and not st.session_state.get("submitted", False):

            missing = False

            # ======================
            # 🚬 吸菸檢查
            # ======================
            if not st.session_state.get("smoke"):
                missing = True

            else:
                smoke = st.session_state.get("smoke")

                if smoke == "每天吸(幾乎)":
                    if not st.session_state.get("smokes") or not st.session_state.get("smokes_years"):
                        missing = True

                if smoke == "已經戒菸":
                    if not st.session_state.get("quit_year") or not st.session_state.get("quit_month"):
                        missing = True

            # ======================
            # 🚬 其他菸品
            # ======================
            if not st.session_state.get("other_smoke"):
                missing = True

            if st.session_state.get("other_smoke") == "是":
                if not st.session_state.get("other_smoke_type"):
                    missing = True

                if "其他" in (st.session_state.get("other_smoke_type") or []):
                    if not st.session_state.get("smokes_other"):
                        missing = True

            # ======================
            # 🍺 飲酒
            # ======================
            if not st.session_state.get("drink1"):
                missing = True

            if st.session_state.get("drink1") and st.session_state.get("drink1") != "未曾飲酒":

                required_drink = [
                    "alcohol_type",
                    "drink2",
                    "drink_freq",
                    "max_drink",
                    "max_drink_type"
                ]

                for k in required_drink:
                    if not st.session_state.get(k):
                        missing = True

                if st.session_state.get("drink4") == "是":
                    if not st.session_state.get("quit_year") or not st.session_state.get("quit_month"):
                        missing = True

            # ======================
            if missing:
                st.error("⚠️ 仍有欄位尚未填寫，請完成所有生活習慣問題")
                st.stop()
        
            st.session_state["submitted"] = True

              # ======================
            # 🔥 組資料
            # ======================
            data = {k: st.session_state.get(k, None) for k in EXPORT_SCHEMA}
            data["record_id"] = str(uuid.uuid4())[:8]
            data["submit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # list → string
            for k, v in data.items():
                if isinstance(v, list):
                    data[k] = ", ".join(map(str, v))

            # ======================
            # 🔥 這一行你現在少掉的關鍵
            # ======================
            save_to_gsheet(data)
            # 5️⃣ 完成頁
            st.session_state.page = "done"
            st.rerun()
if st.session_state.page == "done":
    st.success("問卷已完成！感謝您的填寫 🙏")
from datetime import datetime
st.write(
    "填表日期:",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)






