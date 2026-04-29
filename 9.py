import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
from datetime import date
import gspread   # ✅ 要加這行

import uuid
from datetime import datetime
#終端機輸入streamlit run c:/Users/Jinzer/Desktop/python/問卷收集/10.py
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False

if "page" not in st.session_state:
    st.session_state["page"] = 1
st.title("📊 發展可規模化之台灣胰臟癌高風險族群 臨床試驗/研究受試者問卷")
import streamlit as st
import gspread
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


    sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1Afrj6EkBm1qe0y6RMNjd7wQgAQtTaM1dCO7l_bG1yKQ"
    ).worksheet("工作表1")
      # 👇 就放這裡（重點）
    if sheet.row_values(1) == []:
        sheet.append_row(list(flatten_survey(SCHEMA).keys()))

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

SCHEMA = {
    "pid": None,
    "age": None,
    "gender": None,
    "height": None,
    "weight": None,
    "weight_1y": None,
    "blood_type": None,
    "dob": None,
    "email": None,

    "choices": [],
    "no_disease": False,

    "cancer_type": None,
    "cancer_year": None,
    "cancer_month": None,
    "cancer_age": None,

    "acute_age": None,
    "acute_treat_times": None,

    "chronic_age": None,
    "chronic_treat_times": None,

    "diabetes_type": None,
    "diabetes_age": None,
    "diabetes_treatment": None,

    "exam": None,
    "MRI_treatment": None,

    "answer1": None,
    "answer2": None,
    "gene": None,
    "probiotics": None,
    "antibiotics": None,
    "colonoscopy": None,

    "choices3": [],
    "no_disease3": False,
    "other_sy": None,

    "family": [],   # 👈 重點：結構化 list
    "other_family": [],

    "symptoms": {
        "list": [],
        "no_symptom": False,
        "other": None
    }
}



import json

def flatten_survey(s):
    row = {}

    # ======================
    # 🟦 基本資料
    # ======================
    row["pid"] = s.get("pid")
    row["age"] = s.get("age")
    row["gender"] = s.get("gender")
    row["height"] = s.get("height")
    row["weight"] = s.get("weight")
    row["weight_1y"] = s.get("weight_1y")
    row["blood_type"] = s.get("blood_type")
    row["dob"] = str(s.get("dob"))
    row["email"] = s.get("email")

    # ======================
    # 🟨 既往病史（flatten）
    # ======================
    mh = s.get("medical_history", {})

    row["choices"] = ",".join(s.get("choices", []))
    row["no_disease"] = s.get("no_disease")

    row["cancer_type"] = mh.get("cancer", {}).get("type")
    row["cancer_year"] = mh.get("cancer", {}).get("year")
    row["cancer_month"] = mh.get("cancer", {}).get("month")
    row["cancer_age"] = mh.get("cancer", {}).get("age")

    row["acute_age"] = mh.get("acute_pancreatitis", {}).get("age")
    row["acute_treat_times"] = mh.get("acute_pancreatitis", {}).get("times")

    row["chronic_age"] = mh.get("chronic_pancreatitis", {}).get("age")
    row["chronic_treat_times"] = mh.get("chronic_pancreatitis", {}).get("times")

    diabetes = mh.get("diabetes", {})
    row["diabetes_type"] = diabetes.get("type")
    row["diabetes_age"] = diabetes.get("age")
    row["diabetes_treatment"] = diabetes.get("treatment")

    row["exam"] = mh.get("exam")
    row["MRI_treatment"] = mh.get("MRI_treatment")

    # ======================
    # 🟩 症狀
    # ======================
    row["symptoms_list"] = ",".join(s.get("choices3", []))
    row["symptoms_no"] = s.get("no_disease3")
    row["symptoms_other"] = s.get("other_sy")

    # ======================
    # 🟪 family（展開成 JSON）
    # ======================
    family = mh.get("family", [])
    row["family_json"] = json.dumps(family, ensure_ascii=False)

    row["family_count"] = len(family)

    other_family = mh.get("other_family", [])
    row["other_family_json"] = json.dumps(other_family, ensure_ascii=False)
    row["other_family_count"] = len(other_family)

    # ======================
    # 🟧 lifestyle - smoking
    # ======================
    smoking = s.get("lifestyle", {}).get("smoking", {})

    row["smoke_status"] = smoking.get("status")

    row["smokes_per_day"] = smoking.get("daily", {}).get("cigs_per_day")
    row["smoke_years"] = smoking.get("daily", {}).get("years")

    row["smoke_quit_year"] = smoking.get("quit", {}).get("years_ago")
    row["smoke_quit_month"] = smoking.get("quit", {}).get("months_ago")
    row["smoke_quit_age"] = smoking.get("quit", {}).get("quit_age")

    # other smoking
    row["other_smoke_use"] = smoking.get("other_products", {}).get("use_other")
    row["other_smoke_types"] = ",".join(
        smoking.get("other_products", {}).get("types", [])
    )
    row["other_smoke_text"] = smoking.get("other_products", {}).get("other_text")

    # ======================
    # 🟫 alcohol
    # ======================
    alcohol = s.get("lifestyle", {}).get("alcohol", {})

    row["drink_freq_year"] = alcohol.get("past_year_frequency")
    row["drink_type"] = alcohol.get("main_type")
    row["drink_amount"] = alcohol.get("typical_amount")
    row["binge_freq"] = alcohol.get("binge_frequency")
    row["max_drink"] = alcohol.get("max_amount_lifetime")
    row["max_drink_type"] = alcohol.get("max_amount_type")

    row["alcohol_quit"] = alcohol.get("quit")
    row["alcohol_quit_info"] = json.dumps(alcohol.get("quit_info"), ensure_ascii=False)

    # ======================
    # 🆔 系統欄位
    # ======================
    row["record_id"] = s.get("record_id")
    row["submit_time"] = s.get("submit_time")

    return row
for k, v in SCHEMA.items():
    if k not in st.session_state:
        st.session_state[k] = v
def is_empty(v):
    if v is None:
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    if isinstance(v, list) and len(v) == 0:
        return True
    return False
# 那選項如果是2️⃣ 動態欄位3️⃣ 結構化欄位（dict / list）呢

if st.session_state.page == 1:
    st.header("📌 1. 基本資料")
    st.subheader("請填寫個人基本資料")
    st.divider()
    with st.form("survey"):
        # ===== 個案編號 =====
        pid = st.text_input("個案編號", placeholder="請輸入個案編號", key="pid")
        age = st.number_input("年齡", min_value=1, max_value=120,value=None,placeholder="請輸入年齡",key="age")
        gender= st.selectbox("性別", ["男", "女"],index=None,key="gender")
        height= st.number_input("身高 (公分)", min_value=50, max_value=230,value=None,placeholder="請輸入身高",key="height")
        weight =st.number_input("體重 (公斤)", min_value=1, max_value=230,value=None,placeholder="請輸入體重",key="weight")
        weight_1y =  st.number_input("一年前體重 (公斤)", min_value=1, max_value=230,value=None,placeholder="請輸入一年前體重",key="weight_1y")
        blood_type = st.selectbox("血型", ["A", "B", "AB", "O","Rh","不清楚"],index=None,placeholder="請選擇血型",key="blood_type")
        dob = st.date_input("出生年月日",value=None, min_value=date(1900, 1, 1),max_value=date.today(),key="dob")
        email = st.text_input("E-mail", placeholder="請輸入 email",key="email")
        # if dob:
        #     today = date.today()
        #     agecount = today.year - dob.year - (
        #         (today.month, today.day) < (dob.month, dob.day)
        #     )
        #     st.write(f"年齡: {agecount}")
        #     st.session_state["agecount"] = agecount
        submitted = st.form_submit_button("下一頁 ➡")

        if submitted:
            REQUIRED_FIELDS = [
                "pid",
                "age",
                "gender",
                "height",
                "weight",
                "weight_1y",
                "blood_type",
                "dob",
                "email"
            ]
            missing = [
                k for k in REQUIRED_FIELDS
                if is_empty(st.session_state.get(k))
            ]

            if missing:
                st.error("⚠️ 尚未填寫欄位：")
                st.write(missing)
                st.stop()
            else:
                st.session_state.page = 2
                st.rerun()
        st.divider()
# =========================
# PAGE 2
# =========================

if "medical_history" not in st.session_state:
    st.session_state["medical_history"] = {
        "choices": [],
        "exam": None,
        "MRI_treatment": None,
        "family": [],
        "other_family": []
    }

if "clinical" not in st.session_state:
    st.session_state["clinical"] = {
        "symptoms": {
            "list": [],
            "no_symptom": False,
            "other": None
        }
    }

if "family_history" not in st.session_state:
    st.session_state["family_history"] = {}

if "lifestyle" not in st.session_state:
    st.session_state["lifestyle"] = {
        "smoking": {},
        "alcohol": {}
    }
elif st.session_state.page == 2:
    st.header("📌 2. 既往病史")
    st.subheader("請填寫既往病史")
    st.divider()
  
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

    st.session_state["final_choices"] = final_choices

            
    # =========================
    # 🅰️A選項 → 額外輸入
    # =========================

    if "癌症" in choices:
        with st.expander("🧬 癌症資料"):

            cancer_type = st.text_input(
                "請輸入曾患有的癌症",
                key="cancer_type"
            )
            col1, col2 = st.columns(2)
            with col1:
                cancer_year = st.selectbox(
                    "罹癌___年",
                    [""] + list(range(1, 91)),
                    key="cancer_year"
                )
            with col2:
                cancer_month = st.selectbox(
                    "罹癌___月",
                    [""] + list(range(1, 13)),
                    key="cancer_month"
                )
            if cancer_year == "" or cancer_month == "":
                st.warning("請完整填寫患癌時間")
                st.stop()
            cancer_age = st.number_input(
                "患癌年齡",
                min_value=10,
                max_value=120,
                key="cancer_age"
            )
            # ✅ 統一收集
            st.session_state["medical_history"]["cancer"] = {
                "type": cancer_type,
                "year": cancer_year,
                "month": cancer_month,
                "age": cancer_age
            }
    if "急性胰臟炎" in choices:
        with st.expander("🧪 急性胰臟炎"):

            acute_age = st.number_input(
                "發病年齡",
                min_value=10,
                max_value=120,
                key="acute_age"
            )

            acute_treat_times = st.number_input(
                "治療次數",
                min_value=0,
                max_value=120,
                key="acute_treat_times"
            )

            st.session_state["medical_history"]["acute_pancreatitis"] = {
                "age": acute_age,
                "times": acute_treat_times
            }
    if "慢性胰臟炎" in choices:
        with st.expander("🧪 慢性胰臟炎"):

            chronic_age = st.number_input(
                "發病年齡",
                min_value=10,
                max_value=120,
                key="chronic_age"
            )

            chronic_treat_times = st.number_input(
                "治療次數",
                min_value=0,
                max_value=120,
                key="chronic_treat_times"
            )

            st.session_state["medical_history"]["chronic_pancreatitis"] = {
                "age": chronic_age,
                "times": chronic_treat_times
            }
    if "糖尿病" in choices:
        with st.expander("🩸 糖尿病資料"):
            diabetes_type = st.selectbox(
                "類型",
                ["第一型", "第二型", "不知道"],
                key="diabetes_type"
            )

            diabetes_age = st.number_input(
                "診斷年齡",
                min_value=0,
                max_value=120,
                key="diabetes_age"
            )

            diabetes_treatment = st.selectbox(
                "治療方式",
                ["無", "斷食", "口服藥物", "注射胰島素", "不知道"],
                key="diabetes_treatment"
            )

            st.session_state["medical_history"]["diabetes"] = {
                "type": diabetes_type,
                "age": diabetes_age,
                "treatment": diabetes_treatment
            }                
            st.subheader("若有藥物治療，請後續使用E-mail或Line方式提供藥物名稱")
    st.divider()
        
    exam = st.selectbox("過去一年內是否做過內視鏡超音波或MRI檢查?",
        ["是", "否"],index=None,key="exam")
    MRI_treatment = None
    if exam == "是":
        MRI_treatment = st.selectbox("檢查方式",["MRI", "內視鏡超音波"],
            index=None,key="MRI_treatment")
    st.session_state["medical_history"]["exam"] = exam
    st.session_state["medical_history"]["MRI_treatment"] = MRI_treatment



    answer1 = st.selectbox(
        "胰臟癌症家族病史?",["無", "有"],
        key="answer1",index=None)
    

    # =========================
    # 胰臟癌家族病史
    # =========================
    if "medical_history" not in st.session_state:
        st.session_state["medical_history"] = {}
    if "family" not in st.session_state["medical_history"]:
        st.session_state["medical_history"]["family"] = []
    if answer1 == "有":
        st.markdown("### 👨‍👩‍👧‍👦 家族病史填寫")

        family = st.session_state["medical_history"]["family"]

        # =========================
        # add / remove
        # =========================
        col_add, col_del = st.columns(2)

        with col_add:
            if st.button("➕ 新增一筆", key="add_family"):
                family.append({
                    "age": None,
                    "relation": "",
                    "relation_type": None,
                    "relation_other": None
                })
                st.rerun()

        with col_del:
            if st.button("➖ 刪除一筆", key="del_family"):
                if len(family) > 0:
                    family.pop()
                    st.rerun()

        # =========================
        # render dynamic UI
        # =========================
        for i, f in enumerate(family):
            st.markdown(f"### 第 {i+1} 筆")

            f["age"] = st.number_input(
                "幾歲罹癌",
                min_value=10,
                max_value=120,
                value=f["age"],
                key=f"fam_age_{i}"
            )

            f["relation"] = st.text_input(
                "稱謂",
                value=f["relation"],
                key=f"fam_relation_{i}"
            )

            f["relation_type"] = st.selectbox(
                "與之關係",
                ["一等親", "二等親", "其他"],
                index=0 if f["relation_type"] is None else
                ["一等親", "二等親", "其他"].index(f["relation_type"]),
                key=f"fam_type_{i}"
            )

            if f["relation_type"] == "其他":
                f["relation_other"] = st.text_input(
                    "請填寫關係",
                    value=f.get("relation_other", ""),
                    key=f"fam_other_{i}"
                )
        # 🔥 already structured → no rebuild needed
        st.session_state["medical_history"]["family"] = family
    if "medical_history" not in st.session_state:
        st.session_state["medical_history"] = {}

    if "other_family" not in st.session_state["medical_history"]:
        st.session_state["medical_history"]["other_family"] = []

    answer2 = st.selectbox(
        "其他家族病史?",
        ["無", "有"],
        key="answer2",index=None)
    # =========================
    # 其他家族病史
    # =========================
    if answer2 == "有":
        st.markdown("### 👨‍👩‍👧‍👦 其他家族病史填寫")

        other_family = st.session_state["medical_history"]["other_family"]

        # =========================
        # add / delete
        # =========================
        col_add, col_del = st.columns(2)

        with col_add:
            if st.button("➕ 新增一筆", key="add_other"):
                other_family.append({
                    "age": None,
                    "relation": "",
                    "relation_type": None,
                    "relation_other": ""
                })
                st.rerun()

        with col_del:
            if st.button("➖ 刪除一筆", key="del_other"):
                if len(other_family) > 0:
                    other_family.pop()
                    st.rerun()

        # =========================
        # render
        # =========================
        for i, f in enumerate(other_family):
            st.markdown(f"### 第 {i+1} 筆")

            f["age"] = st.number_input(
                "幾歲罹癌",
                min_value=10,
                max_value=120,
                value=f["age"],
                key=f"other_age_{i}"
            )

            f["relation"] = st.text_input(
                "稱謂（父親/母親/兄弟）",
                value=f["relation"],
                key=f"other_relation_{i}"
            )

            f["relation_type"] = st.selectbox(
                "與之關係",
                ["一等親", "二等親", "其他"],
                index=(
                    0 if f["relation_type"] is None
                    else ["一等親", "二等親", "其他"].index(f["relation_type"])
                ),
                key=f"other_type_{i}"
            )

            if f["relation_type"] == "其他":
                f["relation_other"] = st.text_input(
                    "請填寫與之關係",
                    value=f.get("relation_other", ""),
                    key=f"other_relation_extra_{i}"
                )
        # 🔥 store structured result
        st.session_state["medical_history"]["other_family"] = other_family


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

    # =========================
    # clean data layer
    # =========================
    def build_symptom_payload():
        if st.session_state.get("no_disease3"):
            return {
                "list": [],
                "no_symptom": True,
                "other": None
            }

        raw = st.session_state.get("choices3", [])

        other = None
        if "其他" in raw:
            other = st.session_state.get("other_sy")

        return {
            "list": [x for x in raw if x != "其他"],
            "no_symptom": False,
            "other": other
        }


    # =========================
    # UI for "其他"
    # =========================
    if "其他" in st.session_state.get("choices3", []) and not st.session_state.get("no_disease3"):
        st.text_input(
            "請填寫其他症狀",
            key="other_sy"
        )

    # =========================
    # final output (single source of truth)
    # =========================
    st.session_state["clinical"]["symptoms"] = build_symptom_payload()
    # 🔥 NEW：flatten for Google Sheet
    st.session_state["symptoms_list"] = ",".join(st.session_state.get("choices3", []))
    st.session_state["symptoms_no"] = st.session_state.get("no_disease3")
    st.session_state["symptoms_other"] = st.session_state.get("other_sy")
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
                family = st.session_state["medical_history"].get("family", [])
                st.session_state["family_count"] = len(family)
                st.session_state["family_json"] = family
                other_family = st.session_state["medical_history"].get("other_family", [])
                st.session_state["other_family_count"] = len(other_family)
                st.session_state["other_family_json"] = other_family

            else:
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
        ["從未吸菸", "偶爾吸(不是每天)", "每天吸(幾乎)", "已經戒菸"],
        key="smoke",
        index=None
    )

    # 建立結構
    st.session_state["lifestyle"]["smoking"] = {
        "status": smoke
    }

    # -------------------------
    # 每天吸菸
    # -------------------------
    if smoke == "每天吸(幾乎)":
        avg_smoke = st.number_input(
            "平均每天幾支菸",
            key="smokes",
            min_value=1,
            max_value=120,
            value=None,
            placeholder="請輸入平均每天幾支菸"
        )

        smoke_age = st.number_input(
            "菸齡",
            key="smokes_years",
            min_value=1,
            max_value=120,
            value=None,
            placeholder="請輸入抽菸多少年了"
        )

        st.session_state["lifestyle"]["smoking"]["daily"] = {
            "cigs_per_day": avg_smoke,
            "years": smoke_age
        }

    # -------------------------
    # 已戒菸
    # -------------------------
    if smoke == "已經戒菸":
        col1, col2 = st.columns(2)

        with col1:
            quit_year = st.selectbox(
                "戒菸___年",
                list(range(1, 91)),
                key="quit_year",
                index=None
            )

        with col2:
            quit_month = st.selectbox(
                "戒菸___月",
                list(range(1, 13)),
                key="quit_month",
                index=None
            )

        quit_age = st.number_input(
            "幾歲時戒菸",
            key="quit_age",
            min_value=10,
            max_value=120,
            value=None,
            placeholder="請輸入戒菸時的年齡"
        )

        st.session_state["lifestyle"]["smoking"]["quit"] = {
            "years_ago": quit_year,
            "months_ago": quit_month,
            "quit_age": quit_age
        }

    # -------------------------
    # 其他菸品
    # -------------------------
    other_smoke = st.selectbox(
        "是否使用其他菸品",
        ["否", "是"],
        key="other_smoke",
        index=None
    )

    selected = []

    if other_smoke == "是":
        st.multiselect(
            "其他菸品",
            ["電子菸", "菸斗", "雪茄", "加熱菸", "其他"],
            key="other_smoke_type"
        )

        selected = st.session_state.get("other_smoke_type", [])

    other_text = None
    if "其他" in selected:
        other_text = st.text_input(
            "請描述使用的其他菸品",
            key="smokes_other",
            placeholder="請輸入菸品"
        )

    st.session_state["lifestyle"]["smoking"]["other_products"] = {
        "use_other": other_smoke,
        "types": selected,
        "other_text": other_text
    }
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
        "一個月2-3天", "一個月1天", "一年3-11天", "1年1-2天"
    ]

    drink1 = st.selectbox(
        "2.請問您過去一年喝酒情況?",
        drinking_levels + ["未曾飲酒"],
        index=None,
        key="drink1"
    )

    # 初始化
    st.session_state["lifestyle"]["alcohol"] = {
        "past_year_frequency": drink1
    }

    # -------------------------
    # 有喝酒才展開細節
    # -------------------------
    if drink1 in drinking_levels:

        alcohol_type = st.selectbox(
            "過去一年主要的飲用酒類",
            ["啤酒", "紅酒", "蒸餾酒"],
            index=None,
            key="alcohol_type"
        )

        drink2 = st.selectbox(
            "2-1.請問您過去一年喝的酒精含量(單位:杯)",
            ["25杯以上","19-24杯","16-18杯","12-15杯","9-11杯",
            "7-8杯","5-6杯","3-4杯","2","1"],
            index=None,
            key="drink2"
        )

        gender = st.session_state.get("gender")

        if gender == "男":
            drink_question = "2-2.男生：2小時內喝完5杯等量酒的頻率？"
        elif gender == "女":
            drink_question = "2-2.女生：2小時內喝完4杯等量酒的頻率？"
        else:
            drink_question = "2-2.短時間大量飲酒頻率？"

        drink_freq = st.selectbox(
            drink_question,
            drinking_levels + ["沒有"],
            index=None,
            key="drink_freq"
        )

        max_drink = st.selectbox(
            "2-3.一生中單日最大酒精量(24小時內)",
            ["36杯以上", "24-35杯", "18-23杯", "12-17杯",
            "8-11杯", "5-7杯", "4杯", "3杯", "2杯", "1杯"],
            index=None,
            key="max_drink"
        )

        max_drink_type = st.selectbox(
            "單日最大飲用酒類",
            ["啤酒", "紅酒", "蒸餾酒"],
            index=None,
            key="max_drink_type"
        )

        drink4 = st.selectbox(
            "是否已戒酒?",
            ["否", "是"],
            index=None,
            key="drink4"
        )

        quit_info = None

        if drink4 == "是":
            col1, col2 = st.columns(2)

            with col1:
                alcohol_quit_year = st.selectbox(
                    "戒酒___年",
                    list(range(1, 91)),
                    index=None,
                    key="alcohol_quit_year"
                )

            with col2:
                alcohol_quit_month = st.selectbox(
                    "戒酒___月",
                    list(range(1, 13)),
                    index=None,
                    key="alcohol_quit_month"
                )

            quit_info = {
                "years_ago": alcohol_quit_year,
                "months_ago": alcohol_quit_month
            }

        # 寫入 session_state
        st.session_state["lifestyle"]["alcohol"].update({
            "main_type": alcohol_type,
            "typical_amount": drink2,
            "binge_frequency": drink_freq,
            "max_amount_lifetime": max_drink,
            "max_amount_type": max_drink_type,
            "quit": drink4,
            "quit_info": quit_info
        })
        st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ 上一頁"):
            st.session_state.page = 2
            st.rerun()

    with col2:
        if st.button("✅ 完成問卷"):

            errors = []

            # 吸菸必填
            if not st.session_state.get("smoke"):
                errors.append("請填寫吸菸習慣")

            if not st.session_state.get("other_smoke"):
                errors.append("請填寫其他菸品")

            # 飲酒必填
            if not st.session_state.get("drink1"):
                errors.append("請填寫飲酒習慣")

            # 有喝酒要補完整
            if st.session_state.get("drink1") != "未曾飲酒":

                req = [
                    "alcohol_type",
                    "drink2",
                    "drink_freq",
                    "max_drink",
                    "max_drink_type",
                    "drink4"
                ]

                for r in req:
                    if not st.session_state.get(r):
                        errors.append(f"{r} 未填")

            if errors:
                for e in errors:
                    st.error(e)
                st.stop()
            st.session_state["smoke_status"] = smoke
            st.session_state["smokes_per_day"] = avg_smoke if smoke == "每天吸(幾乎)" else None
            st.session_state["smoke_years"] = smoke_age if smoke == "每天吸(幾乎)" else None

            st.session_state["smoke_quit_year"] = quit_year if smoke == "已經戒菸" else None
            st.session_state["smoke_quit_month"] = quit_month if smoke == "已經戒菸" else None
            st.session_state["smoke_quit_age"] = quit_age if smoke == "已經戒菸" else None

            st.session_state["drink_freq_year"] = drink1
            st.session_state["drink_type"] = alcohol_type if drink1 != "未曾飲酒" else None
            st.session_state["drink_amount"] = drink2 if drink1 != "未曾飲酒" else None
            st.session_state["binge_freq"] = drink_freq if drink1 != "未曾飲酒" else None
            st.session_state["max_drink"] = max_drink if drink1 != "未曾飲酒" else None

            # =====================
            # 建立輸出資料
            # =====================
            st.session_state["record_id"] = str(uuid.uuid4())[:8]
            st.session_state["submit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 🔥 建議：先 copy 一份乾淨 state
            clean_state = dict(st.session_state)

            data = flatten_survey(clean_state)
            save_to_gsheet(data)

            st.success("問卷已完成，感謝您！")

            st.session_state.page = "done"
            st.rerun()
if st.session_state.page == "done":
    st.success("問卷已完成！感謝您的填寫 🙏")
from datetime import datetime
if "survey_time" not in st.session_state:
    st.session_state["survey_time"] = datetime.now()

st.write(
    "填表日期:",
    st.session_state["survey_time"].strftime("%Y-%m-%d %H:%M:%S")
)





