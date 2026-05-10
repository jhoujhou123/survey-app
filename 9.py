import json 
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
from datetime import date
import gspread   # ✅ 要加這行
    
import uuid
from datetime import datetime
#終端機輸入streamlit run c:/Users/Jinzer/Desktop/python/問卷收集/14.py
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False

if "page" not in st.session_state:
    st.session_state["page"] = 1
st.title("📊 發展可規模化之台灣胰臟癌高風險族群 臨床試驗/研究受試者問卷")
from google.oauth2.service_account import Credentials
# ======================
# 🔐 Google Sheets 設定
# ======================
def init_gsheet():
    import gspread
    from google.oauth2.service_account import Credentials

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # creds = Credentials.from_service_account_file(
    #     "dogwood-cinema-494201-u6-248629932a97.json",
    #     scopes=scope
    # )
    creds = Credentials.from_service_account_file(
    r"C:\Users\Jinzer\Desktop\python\問卷收集\dogwood-cinema-494201-u6-248629932a97.json",
    scopes=scope
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(
        "1Afrj6EkBm1qe0y6RMNjd7wQgAQtTaM1dCO7l_bG1yKQ"
    ).sheet1

    return sheet
# ======================
# 💾 寫入 Google Sheet
# ======================
def save_to_gsheet(data):

    import json
    import pandas as pd
    from datetime import date, datetime
    st.write("DEBUG json:", json)

    sheet = init_gsheet()

    headers = sheet.row_values(1)



    # 自動新增新欄位
    new_cols = [k for k in data.keys() if k not in headers]

    if new_cols:
        headers.extend(new_cols)

        sheet.update(
            "1:1",
            [headers]
        )

    # 第一份資料
    if not headers:
        headers = list(data.keys())
        sheet.append_row(headers)


    row = []

    for h in headers:
        v = data.get(h, "")

        # dict / list
        if isinstance(v, (dict, list)):
            v = json.dumps(v, ensure_ascii=False)

        elif isinstance(v, (date, datetime)):
            v = str(v)

        elif v is None:
            v = ""

        else:
            # pandas NaN protection
            try:
                if pd.isna(v):
                    v = ""
            except:
                pass

        row.append(v)

    sheet.append_row(row)
# ======================
# 🧠 清理資料（核心）
# ======================

def build_clean_data():

    data = {}

    # =========================
    # 0️⃣ 系統欄位
    # =========================
    data["record_id"] = str(uuid.uuid4())[:8]
    data["submit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # =========================
    # 1️⃣ 基本資料
    # =========================
    data["pid"] = st.session_state.get("pid")
    data["age"] = st.session_state.get("age")
    data["gender"] = st.session_state.get("gender")
    data["height"] = st.session_state.get("height")
    data["weight"] = st.session_state.get("weight")
    data["weight_1y"] = st.session_state.get("weight_1y")
    data["blood_type"] = st.session_state.get("blood_type")
    data["email"] = st.session_state.get("email")
    data["akknote"] = st.session_state.get("akknote")

    dob = st.session_state.get("dob")
    data["dob"] = str(dob) if dob else None



    # BMI
    try:
        if data["height"] and data["weight"]:
            h = data["height"] / 100
            data["bmi"] = round(data["weight"] / (h ** 2), 2)
        else:
            data["bmi"] = None
    except:
        data["bmi"] = None

    # =========================
    # 2️⃣ 慢性病
    # =========================
    diseases = st.session_state.get("final_choices") or []
    data["diseases"] = diseases
    data["no_disease"] = st.session_state.get("no_disease", False)

    data["dm_flag"] = int("糖尿病" in diseases)
    data["cancer_flag"] = int("癌症" in diseases)
    data["pancreatitis_flag"] = int(
        "急性胰臟炎" in diseases or "慢性胰臟炎" in diseases
    )

    # =========================
    # 3️⃣ 疾病細節（raw dict）
    # =========================
    data["cancer"] = {
        "type": st.session_state.get("cancer_type"),
        "year": st.session_state.get("cancer_year"),
        "month": st.session_state.get("cancer_month"),
        "age": st.session_state.get("cancer_age")
    }

    data["acute_pancreatitis"] = {
        "age": st.session_state.get("acute_age"),
        "times": st.session_state.get("acute_treat_times")
    }

    data["chronic_pancreatitis"] = {
        "age": st.session_state.get("chronic_age"),
        "times": st.session_state.get("chronic_treat_times")
    }

    data["diabetes"] = {
        "type": st.session_state.get("diabetes_type"),
        "age": st.session_state.get("diabetes_age"),
        "treatment": st.session_state.get("diabetes_treatment")
    }

    # =========================
    # 4️⃣ 檢查
    # =========================
    data["exam"] = st.session_state.get("exam")
    data["exam_type"] = st.session_state.get("MRI_treatment")

    # =========================
    # 5️⃣ 家族病史（SAFE version）
    # =========================
    family_count = st.session_state.get("family_count") or 0
    pancreatic_family = []

    for i in range(int(family_count)):
        pancreatic_family.append({
            "age": st.session_state.get(f"page3_cancer_age_{i}"),
            "relation": st.session_state.get(f"page3_relation_{i}"),
            "type": st.session_state.get(f"page3_relation_type_{i}"),
            "other": st.session_state.get(f"page3_relation_other_{i}")
        })

    data["pancreatic_family_history"] = pancreatic_family

    other_count = st.session_state.get("other_count") or 0
    other_family = []

    for i in range(int(other_count)):
        other_family.append({
            "age": st.session_state.get(f"other_cancer_age_{i}"),
            "relation": st.session_state.get(f"other_relation_{i}"),
            "type": st.session_state.get(f"other_relation_type_{i}"),
            "other": st.session_state.get(f"other_relation_other_{i}")
        })

    data["other_family_history"] = other_family

    # =========================
    # 6️⃣ 其他
    # =========================
    data["gene_test"] = st.session_state.get("gene")
    data["probiotics"] = st.session_state.get("probiotics")
    data["antibiotics"] = st.session_state.get("antibiotics")
    data["colonoscopy"] = st.session_state.get("colonoscopy")

    # =========================
    # 7️⃣ 症狀
    # =========================
    data["symptoms"] = st.session_state.get("final_choices3") or {
        "symptoms": [],
        "no_symptom": None,
        "other_symptom": None
    }

    # =========================
    # 8️⃣ 吸菸
    # =========================
    data["smoke"] = st.session_state.get("smoke")

    if data["smoke"] == "每天吸(幾乎)":
        data["avg_smoke"] = st.session_state.get("smokes")
        data["smoke_years"] = st.session_state.get("smokes_years")

    if data["smoke"] == "已經戒菸":
        data["quit_smoke_year"] = st.session_state.get("quit_smoke_year")
        data["quit_smoke_month"] = st.session_state.get("quit_smoke_month")
        data["quit_smoke_age"] = st.session_state.get("quit_smoke_age")

    # =========================
    # 9️⃣ 其他菸品
    # =========================
    data["other_smoke"] = st.session_state.get("other_smoke")

    other_type = st.session_state.get("other_smoke_type") or []
    data["other_smoke_type"] = other_type
    data["other_smoke_desc"] = st.session_state.get("smokes_other") if "其他" in other_type else None

    # =========================
    # 🔟 飲酒
    # =========================
    drink1 = st.session_state.get("drink1")
    data["drink1"] = drink1

    drinking_levels = [
        "每天", "一周5-6天", "一周3-4天", "一周2天", "一周1天",
        "一個月2-3天", "一個月1天", "一年3-11天", "1年1-2天"
    ]

    if drink1 in drinking_levels:
        data["drink_flag"] = 1
        data["alcohol_type"] = st.session_state.get("alcohol_type")
        data["drink2"] = st.session_state.get("drink2")
        data["drink_freq"] = st.session_state.get("drink_freq")
        data["max_drink"] = st.session_state.get("max_drink")
        data["max_drink_type"] = st.session_state.get("max_drink_type")

        if st.session_state.get("drink4") == "是":
            data["quit_alcohol_year"] = st.session_state.get("quit_alcohol_year")
            data["quit_alcohol_month"] = st.session_state.get("quit_alcohol_month")
    else:
        data["drink_flag"] = 0

    return data
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


if st.session_state.page == 1:
    st.header("📌 1. 基本資料")
    st.subheader("請填寫個人基本資料")
    st.divider()
    # if "bnote" not in st.session_state:
    #     st.session_state["bnote"] = ""
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
        st.divider()
        akknote =st.text_input("備註", placeholder="此欄位不需輸入")
        # st.session_state.pop("akknote", None)

        # st.write(st.session_state.get("aanote"))
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
                st.session_state.update({
                "pid": pid,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "weight_1y": weight_1y,
                "blood_type": blood_type,
                "dob": dob,
                "email": email,
                "akknote": akknote
                })
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

# =========================
# PAGE 2
# =========================
elif st.session_state.page == 2:
    st.header("📌 2. 既往病史")
    st.subheader("請填寫既往病史")
    st.divider()
    # =========================
    # ☑️ 主複選題
    # =========================
    # def clear_choices():
    #     st.session_state["choices"] = []
    # no_disease = st.checkbox(
    #     "以上皆無",
    #     on_change=clear_choices
    # )
    # choices = st.multiselect(
    #     "您是否曾患有下列慢性疾病（請在適當項目前打勾）",
    #     ["高血壓", "心臟病", "癌症", "急性胰臟炎", "慢性胰臟炎", "糖尿病"],
    #     key="choices",
    #     disabled=no_disease
    # )
    # def clear_choices():
    #     st.session_state["choices"] = []

    # no_disease = st.checkbox(
    #     "以上皆無",
    #     on_change=clear_choices
    # )

    # choices = st.multiselect(
    #     "慢性疾病",
    #     ["高血壓", "心臟病", "癌症", "急性胰臟炎", "慢性胰臟炎", "糖尿病"],
    #     key="choices",
    #     disabled=no_disease
    # )

    # final_choices = [] if no_disease else choices
    # st.session_state["final_choices"] = final_choices

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

    st.session_state["final_choices"] = final_choices



    # =========================
    # 邏輯處理（互斥）
    # =========================
     # =========================
    # 「以上皆無」互斥
    # =========================
    # if "以上皆無" in choices and len(choices) > 1:
    #     choices = ["以上皆無"]
    #     st.session_state.choices = choices

    # if "以上皆無" in choices:
    #     st.info("已選擇『以上皆無』，其他疾病將忽略")

     
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
    MAX_FAMILY = 5
    if answer1 == "有":
        st.markdown("### 👨‍👩‍👧‍👦 家族病史填寫")
        # 初始化
        if "family_count" not in st.session_state:
            st.session_state.family_count = 1

        # =========================
        # ➕ 新增
        # =========================
        if st.button("➕ 新增一筆家族資料"):
            if st.session_state.family_count < MAX_FAMILY:
                st.session_state.family_count += 1
            else:
                st.warning(f"最多只能新增 {MAX_FAMILY} 筆")

        # =========================
        # 🔁 每一筆
        # =========================
        for i in range(st.session_state.family_count):

            with st.container(border=True):
                col_title, col_del = st.columns([4, 1])

                with col_title:
                    st.markdown(f"#### 第 {i+1} 筆")

                # =========================
                # ❌ 單筆刪除（重點）
                # =========================
                with col_del:
                    if st.button("❌", key=f"del_{i}"):
                        # 刪除該筆資料（shift後面資料）
                        for j in range(i, st.session_state.family_count - 1):
                            for field in ["cancer_age", "relation", "relation_type", "relation_other"]:
                                st.session_state[f"page3_{field}_{j}"] = st.session_state.get(
                                    f"page3_{field}_{j+1}"
                                )

                        # 清掉最後一筆
                        last = st.session_state.family_count - 1
                        for field in ["cancer_age", "relation", "relation_type", "relation_other"]:
                            st.session_state.pop(f"page3_{field}_{last}", None)

                        st.session_state.family_count -= 1
                        st.rerun()

                # =========================
                # 欄位
                # =========================
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

                relation_type = st.selectbox(
                    "與之關係",
                    ["一等親", "二等親", "其他"],
                    key=f"page3_relation_type_{i}"
                )

                if relation_type == "其他":
                    st.text_input(
                        "請填寫與之關係",
                        key=f"page3_relation_other_{i}"
                    )
    MAX_OTHER = 5
    answer2 = st.selectbox(
        "其他家族病史?",
        ["無", "有"],
        key="answer2",
        index=None
    )
    if answer2 == "有":
        st.markdown("### 👨‍👩‍👧‍👦 其他家族病史填寫")

        # 初始化
        if "other_count" not in st.session_state:
            st.session_state.other_count = 1

        # =========================
        # ➕ 新增
        # =========================
        if st.button("➕ 新增一筆家族資料（其他）"):
            if st.session_state.other_count < MAX_OTHER:
                st.session_state.other_count += 1
            else:
                st.warning(f"最多只能新增 {MAX_OTHER} 筆")

        # =========================
        # 🔁 每一筆
        # =========================
        for i in range(st.session_state.other_count):

            with st.container(border=True):
                col_title, col_del = st.columns([4, 1])

                with col_title:
                    st.markdown(f"#### 第 {i+1} 筆")

                # =========================
                # ❌ 單筆刪除（關鍵）
                # =========================
                with col_del:
                    if st.button("❌", key=f"del_other_{i}"):

                        # shift 後面資料往前補
                        for j in range(i, st.session_state.other_count - 1):
                            for field in ["cancer_age", "relation", "relation_type", "relation_other"]:
                                st.session_state[f"other_{field}_{j}"] = st.session_state.get(
                                    f"other_{field}_{j+1}"
                                )

                        # 清掉最後一筆
                        last = st.session_state.other_count - 1
                        for field in ["cancer_age", "relation", "relation_type", "relation_other"]:
                            st.session_state.pop(f"other_{field}_{last}", None)

                        st.session_state.other_count -= 1
                        st.rerun()

                # =========================
                # 欄位
                # =========================
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

                relation_type = st.selectbox(
                    "與之關係",
                    ["一等親", "二等親", "其他"],
                    key=f"other_relation_type_{i}"
                )

                if relation_type == "其他":
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
                # ======================
                clean_data = build_clean_data()
                st.session_state["clean_data"] = clean_data
                # ======================
                # ✅ 2. 標記已送出（可選但推薦）
                # ======================
                # st.session_state["submitted"] = True
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
            st.selectbox("戒菸___年", list(range(1, 91)), key="quit_smoke_year",index=None)
        with col2:
            st.selectbox("戒菸___月", list(range(1, 13)), key="quit_smoke_month",index=None)
        st.number_input("幾歲時戒菸", key="quit_smoke_age", min_value=10, max_value=120,value=None,placeholder="請輸入戒菸時的年齡")
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
        if st.button("✅ 完成問卷"):

            st.write("1️⃣ 按鈕有觸發")

            missing = False

            # ======================
            # 🚬 吸菸檢查
            # ======================
            if not st.session_state.get("smoke"):
                missing = True

            # ======================
            # 🚬 其他菸品
            # ======================
            if not st.session_state.get("other_smoke"):
                missing = True

            # ======================
            # 🍺 飲酒
            # ======================
            if not st.session_state.get("drink1"):
                missing = True

            if missing:
                st.error("⚠️ 有欄位沒填")
                st.stop()

            st.write("2️⃣ 開始 build data")

            try:
                data = build_clean_data()

                st.write("3️⃣ build 成功")
                st.write(data)

            except Exception as e:
                st.error(f"build_clean_data 錯誤: {e}")
                st.stop()

            st.write("4️⃣ 開始寫入 Google Sheet")

            import traceback
            try:

                st.write("A")
                sheet = init_gsheet()

                st.write("B")

                save_to_gsheet(data)

                st.success("✅ 已成功寫入 Google Sheets")

            except Exception as e:

                st.error(f"Google Sheet 錯誤: {e}")

                st.code(traceback.format_exc())

                st.stop()

            st.write("5️⃣ 準備跳轉 done page")

            st.session_state.page = "done"

            st.rerun()

if st.session_state.page == "done":
    st.success("問卷已完成！感謝您的填寫 🙏")
from datetime import datetime
st.write(
    "填表日期:",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)







