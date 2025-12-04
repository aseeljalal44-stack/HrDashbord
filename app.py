"""
لوحة تحكم الموارد البشرية الذكية - تعمل مع أي ملف Excel
الإصدار: 2.0.1 - بدون scipy
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from modules.file_loader import SmartFileLoader
from modules.column_mapper import AutoColumnMapper
from modules.data_analyzer import FlexibleDataAnalyzer
from modules.smart_visualizer import SmartVisualizer

# إعدادات الصفحة
st.set_page_config(
    page_title="لوحة تحكم HR الذكية",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحميل CSS
def load_css():
    css = """
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .upload-box {
        border: 2px dashed #4c51bf;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        background: #f7fafc;
        margin: 20px 0;
    }
    
    .column-map-item {
        background: #edf2f7;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# تهيئة حالة الجلسة
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'column_mapping' not in st.session_state:
    st.session_state.column_mapping = {}
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# العنوان الرئيسي
st.markdown("""
<div class="main-header">
    <h1>📊 لوحة تحكم الموارد البشرية الذكية</h1>
    <p>تعمل مع <strong>أي ملف Excel</strong> - قم برفع ملفك وسنكتشف البيانات تلقائياً</p>
</div>
""", unsafe_allow_html=True)

# الشريط الجانبي
with st.sidebar:
    st.markdown("### ⚙️ إعدادات")
    
    # خيارات اللغة
    language = st.radio("اللغة:", ["العربية", "English"], horizontal=True)
    
    # خيارات السمة
    theme = st.radio("المظهر:", ["فاتح", "مظلم"], horizontal=True)
    
    st.divider()
    
    # تحميل الإعدادات السابقة
    if st.button("📥 تحميل إعدادات سابقة", use_container_width=True):
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                st.session_state.column_mapping = config.get('column_mapping', {})
                st.success("تم تحميل الإعدادات السابقة")
        else:
            st.warning("لا توجد إعدادات سابقة")
    
    # حفظ الإعدادات
    if st.session_state.column_mapping:
        if st.button("💾 حفظ الإعدادات", use_container_width=True):
            config = {
                'column_mapping': st.session_state.column_mapping,
                'saved_at': datetime.now().isoformat()
            }
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            st.success("تم حفظ الإعدادات")

# الصفحة الرئيسية - تحميل الملف
st.markdown("## 📤 الخطوة 1: رفع ملف Excel")

uploaded_file = st.file_uploader(
    "اسحب وأفلت ملف Excel هنا أو انقر للاختيار",
    type=['xlsx', 'xls', 'csv'],
    help="يدعم الملفات: Excel (.xlsx, .xls), CSV"
)

if uploaded_file is not None:
    try:
        # تحميل الملف باستخدام المنظم الذكي
        loader = SmartFileLoader(uploaded_file)
        df = loader.load_file()
        st.session_state.df = df
        st.session_state.file_uploaded = True
        
        st.success(f"✅ تم تحميل الملف بنجاح! ({len(df)} سطر، {len(df.columns)} عمود)")
        
        # عرض عينة من البيانات
        with st.expander("👀 معاينة البيانات (أول 5 صفوف)"):
            st.dataframe(df.head(), use_container_width=True)
        
        # عرض معلومات الأعمدة
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد السجلات", len(df))
        with col2:
            st.metric("عدد الأعمدة", len(df.columns))
        with col3:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            st.metric("أعمدة رقمية", len(numeric_cols))
        
    except Exception as e:
        st.error(f"❌ خطأ في تحميل الملف: {str(e)}")

# إذا تم تحميل الملف، انتقل إلى تعيين الأعمدة
if st.session_state.file_uploaded and st.session_state.df is not None:
    st.markdown("## 🎯 الخطوة 2: تعيين الأعمدة")
    
    df = st.session_state.df
    columns = df.columns.tolist()
    
    # التعرف التلقائي على الأعمدة
    mapper = AutoColumnMapper(df)
    auto_suggestions = mapper.auto_detect_columns()
    
    st.info("""
    💡 **التعرف التلقائي**: النظام حاول تخمين أنواع الأعمدة. يمكنك تعديلها يدوياً إذا كانت غير صحيحة.
    """)
    
    # إنشاء تخطيط تعيين الأعمدة
    column_mapping = {}
    
    # المجموعات الرئيسية للأعمدة
    categories = {
        "معلومات الموظف": ["employee_name", "employee_id", "department", "position", "hire_date"],
        "المالية": ["salary", "allowances", "bonus", "tax"],
        "الأداء": ["performance_score", "kpi", "rating", "review_date"],
        "الحضور": ["attendance_days", "absent_days", "late_days", "overtime_hours"],
        "التدريب": ["trainings_completed", "training_hours", "certifications"],
        "المتابعة": ["manager", "location", "employment_type", "status"]
    }
    
    # عرض تعيين الأعمدة لكل فئة
    for category, fields in categories.items():
        st.markdown(f"### {category}")
        
        cols = st.columns(3)
        for idx, field in enumerate(fields):
            with cols[idx % 3]:
                # اقتراح تلقائي إن وجد
                suggested_column = auto_suggestions.get(field, "غير محدد")
                
                # إنشاء selectbox مع الاقتراح التلقائي كخيار أول
                options = ["❌ لا يوجد"] + columns
                default_idx = 0
                if suggested_column in columns:
                    default_idx = columns.index(suggested_column) + 1
                
                selected = st.selectbox(
                    f"**{field.replace('_', ' ').title()}**",
                    options=options,
                    index=default_idx,
                    key=f"map_{field}"
                )
                
                if selected != "❌ لا يوجد":
                    column_mapping[field] = selected
    
    st.session_state.column_mapping = column_mapping
    
    # زر للمتابعة للتحليل
    if st.button("🚀 انتقل إلى التحليل", type="primary", use_container_width=True):
        st.session_state.analysis_ready = True
        st.rerun()

# إذا كان التحليل جاهزاً
if st.session_state.get('analysis_ready', False):
    st.markdown("## 📊 الخطوة 3: تحليل البيانات الذكي")
    
    analyzer = FlexibleDataAnalyzer(
        st.session_state.df, 
        st.session_state.column_mapping
    )
    
    # التحليل الذكي للبيانات
    analysis = analyzer.analyze_all()
    st.session_state.analysis_results = analysis
    
    # عرض النتائج الرئيسية
    st.markdown("### 📈 النتائج الرئيسية")
    
    # بطاقات KPIs
    kpis = analysis.get('kpis', {})
    if kpis:
        cols = st.columns(4)
        kpi_keys = list(kpis.keys())[:4]
        
        for idx, (col, kpi_key) in enumerate(zip(cols, kpi_keys)):
            with col:
                value = kpis[kpi_key]['value']
                label = kpis[kpi_key]['label']
                
                st.markdown(f"""
                <div class="kpi-card">
                    <div style="font-size: 2rem; margin-bottom: 10px;">
                        {kpis[kpi_key].get('icon', '📊')}
                    </div>
                    <div style="font-size: 2rem; font-weight: bold; color: #3B82F6;">
                        {value}
                    </div>
                    <div style="color: #6B7280;">
                        {label}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # الرسوم البيانية الذكية
    st.markdown("### 📊 الرسوم البيانية التلقائية")
    
    visualizer = SmartVisualizer(
        st.session_state.df,
        st.session_state.column_mapping,
        analysis
    )
    
    # عرض الرسوم حسب توفر البيانات
    charts = visualizer.generate_all_charts()
    
    for chart_info in charts:
        if chart_info['available']:
            st.markdown(f"#### {chart_info['title']}")
            st.plotly_chart(chart_info['figure'], use_container_width=True)
    
    # تحليل إضافي
    with st.expander("🔍 تحليل متقدم"):
        st.markdown("### تحليل متقدم")
        
        # تحليل العلاقات
        numeric_cols = []
        for col in st.session_state.df.columns:
            if pd.api.types.is_numeric_dtype(st.session_state.df[col]):
                numeric_cols.append(col)
        
        if len(numeric_cols) >= 2:
            st.markdown("#### العلاقات بين المتغيرات")
            
            # خريطة حرارية للعلاقات
            numeric_df = st.session_state.df[numeric_cols]
            corr_matrix = numeric_df.corr()
            
            import plotly.express as px
            fig = px.imshow(
                corr_matrix,
                text_auto='.2f',
                color_continuous_scale='RdBu',
                aspect="auto",
                title='خريطة حرارية للعلاقات'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # اكتشاف القيم الشاذة باستخدام numpy فقط (بدون scipy)
        st.markdown("#### اكتشاف القيم الشاذة")
        if 'salary' in st.session_state.column_mapping:
            salary_col = st.session_state.column_mapping['salary']
            if salary_col in st.session_state.df.columns:
                try:
                    salary_data = st.session_state.df[salary_col].dropna()
                    
                    if len(salary_data) > 0:
                        # حساب z-score يدويًا باستخدام numpy
                        mean_salary = salary_data.mean()
                        std_salary = salary_data.std()
                        
                        if std_salary > 0:  # تجنب القسمة على صفر
                            z_scores = np.abs((salary_data - mean_salary) / std_salary)
                            outliers_mask = z_scores > 3
                            outliers = st.session_state.df.loc[salary_data.index[outliers_mask]]
                            
                            if len(outliers) > 0:
                                st.warning(f"تم اكتشاف {len(outliers)} قيمة شاذة في الرواتب")
                                st.dataframe(outliers[[salary_col]], use_container_width=True)
                            else:
                                st.success("✅ لم يتم اكتشاف قيم شاذة في الرواتب")
                        else:
                            st.info("الانحراف المعياري للرواتب صفر، لا يمكن اكتشاف قيم شاذة")
                except Exception as e:
                    st.error(f"خطأ في اكتشاف القيم الشاذة: {str(e)}")
    
    # تحميل التقارير
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # تصدير البيانات المعدلة
        if st.button("📥 تحميل البيانات المعدلة (CSV)", use_container_width=True):
            modified_df = analyzer.get_modified_dataframe()
            csv = modified_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ انقر للتحميل",
                data=csv,
                file_name="hr_data_modified.csv",
                mime="text/csv"
            )
    
    with col2:
        # تصدير التقرير
        if st.button("📄 تحميل التقرير الكامل", use_container_width=True):
            report = analyzer.generate_report()
            st.download_button(
                label="⬇️ انقر للتحميل",
                data=report,
                file_name="hr_analysis_report.txt",
                mime="text/plain"
            )