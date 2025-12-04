"""
لوحة تحكم الموارد البشرية الذكية - تعمل مع أي ملف Excel
الإصدار: 2.1.0 - مع تبديل لغة كامل
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

# ==================== نظام الترجمة الكامل ====================
class TranslationSystem:
    """نظام الترجمة ثنائي اللغة"""
    
    translations = {
        'ar': {
            # العنوان الرئيسي
            'main_title': '📊 لوحة تحكم الموارد البشرية الذكية',
            'main_subtitle': 'تعمل مع <strong>أي ملف Excel</strong> - قم برفع ملفك وسنكتشف البيانات تلقائياً',
            
            # الشريط الجانبي
            'sidebar_settings': '⚙️ إعدادات',
            'sidebar_language': 'اللغة:',
            'sidebar_theme': 'المظهر:',
            'sidebar_load_settings': '📥 تحميل إعدادات سابقة',
            'sidebar_save_settings': '💾 حفظ الإعدادات',
            'sidebar_load_success': 'تم تحميل الإعدادات السابقة',
            'sidebar_save_success': 'تم حفظ الإعدادات',
            'sidebar_no_settings': 'لا توجد إعدادات سابقة',
            
            # رفع الملف
            'upload_title': '📤 الخطوة 1: رفع ملف Excel',
            'upload_placeholder': 'اسحب وأفلت ملف Excel هنا أو انقر للاختيار',
            'upload_help': 'يدعم الملفات: Excel (.xlsx, .xls), CSV',
            'upload_success': '✅ تم تحميل الملف بنجاح!',
            'upload_error': '❌ خطأ في تحميل الملف:',
            'preview_data': '👀 معاينة البيانات (أول 5 صفوف)',
            
            # إحصائيات
            'stats_records': 'عدد السجلات',
            'stats_columns': 'عدد الأعمدة',
            'stats_numeric': 'أعمدة رقمية',
            
            # تعيين الأعمدة
            'mapping_title': '🎯 الخطوة 2: تعيين الأعمدة',
            'mapping_auto': '💡 <strong>التعرف التلقائي</strong>: النظام حاول تخمين أنواع الأعمدة. يمكنك تعديلها يدوياً إذا كانت غير صحيحة.',
            
            # فئات الأعمدة
            'cat_employee_info': 'معلومات الموظف',
            'cat_financial': 'المالية',
            'cat_performance': 'الأداء',
            'cat_attendance': 'الحضور',
            'cat_training': 'التدريب',
            'cat_management': 'المتابعة',
            
            # أسماء الحقول
            'field_employee_name': 'اسم الموظف',
            'field_employee_id': 'رقم الموظف',
            'field_department': 'القسم',
            'field_position': 'المنصب',
            'field_hire_date': 'تاريخ التعيين',
            'field_salary': 'الراتب',
            'field_allowances': 'البدلات',
            'field_bonus': 'المكافأة',
            'field_tax': 'الضريبة',
            'field_performance_score': 'درجة الأداء',
            'field_kpi': 'KPI',
            'field_rating': 'التقييم',
            'field_review_date': 'تاريخ المراجعة',
            'field_attendance_days': 'أيام الحضور',
            'field_absent_days': 'أيام الغياب',
            'field_late_days': 'أيام التأخير',
            'field_overtime_hours': 'ساعات إضافية',
            'field_trainings_completed': 'التدريبات المكتملة',
            'field_training_hours': 'ساعات التدريب',
            'field_certifications': 'الشهادات',
            'field_manager': 'المدير',
            'field_location': 'الموقع',
            'field_employment_type': 'نوع التوظيف',
            'field_status': 'الحالة',
            
            # زر التحليل
            'analyze_button': '🚀 انتقل إلى التحليل',
            
            # نتائج التحليل
            'analysis_title': '📊 الخطوة 3: تحليل البيانات الذكي',
            'kpis_title': '📈 النتائج الرئيسية',
            'charts_title': '📊 الرسوم البيانية التلقائية',
            'advanced_title': '🔍 تحليل متقدم',
            'correlations_title': 'العلاقات بين المتغيرات',
            'outliers_title': 'اكتشاف القيم الشاذة',
            'outliers_found': 'تم اكتشاف {} قيمة شاذة في الرواتب',
            'no_outliers': '✅ لم يتم اكتشاف قيم شاذة في الرواتب',
            'zero_std': 'الانحراف المعياري للرواتب صفر، لا يمكن اكتشاف قيم شاذة',
            
            # تصدير
            'export_data': '📥 تحميل البيانات المعدلة (CSV)',
            'export_report': '📄 تحميل التقرير الكامل',
            'download_csv': '⬇️ انقر للتحميل',
            'download_report': '⬇️ انقر للتحميل',
            
            # رسائل أخرى
            'loading': 'جاري التحميل...',
            'not_available': 'غير متوفر',
        },
        'en': {
            # Main Title
            'main_title': '📊 Smart HR Analytics Dashboard',
            'main_subtitle': 'Works with <strong>any Excel file</strong> - Upload your file and we will automatically detect data',
            
            # Sidebar
            'sidebar_settings': '⚙️ Settings',
            'sidebar_language': 'Language:',
            'sidebar_theme': 'Theme:',
            'sidebar_load_settings': '📥 Load Previous Settings',
            'sidebar_save_settings': '💾 Save Settings',
            'sidebar_load_success': 'Previous settings loaded',
            'sidebar_save_success': 'Settings saved',
            'sidebar_no_settings': 'No previous settings',
            
            # File Upload
            'upload_title': '📤 Step 1: Upload Excel File',
            'upload_placeholder': 'Drag and drop Excel file here or click to browse',
            'upload_help': 'Supports: Excel (.xlsx, .xls), CSV',
            'upload_success': '✅ File uploaded successfully!',
            'upload_error': '❌ Error loading file:',
            'preview_data': '👀 Data Preview (First 5 rows)',
            
            # Statistics
            'stats_records': 'Number of Records',
            'stats_columns': 'Number of Columns',
            'stats_numeric': 'Numeric Columns',
            
            # Column Mapping
            'mapping_title': '🎯 Step 2: Map Columns',
            'mapping_auto': '💡 <strong>Auto-detection</strong>: System tried to guess column types. You can adjust manually if incorrect.',
            
            # Column Categories
            'cat_employee_info': 'Employee Information',
            'cat_financial': 'Financial',
            'cat_performance': 'Performance',
            'cat_attendance': 'Attendance',
            'cat_training': 'Training',
            'cat_management': 'Management',
            
            # Field Names
            'field_employee_name': 'Employee Name',
            'field_employee_id': 'Employee ID',
            'field_department': 'Department',
            'field_position': 'Position',
            'field_hire_date': 'Hire Date',
            'field_salary': 'Salary',
            'field_allowances': 'Allowances',
            'field_bonus': 'Bonus',
            'field_tax': 'Tax',
            'field_performance_score': 'Performance Score',
            'field_kpi': 'KPI',
            'field_rating': 'Rating',
            'field_review_date': 'Review Date',
            'field_attendance_days': 'Attendance Days',
            'field_absent_days': 'Absent Days',
            'field_late_days': 'Late Days',
            'field_overtime_hours': 'Overtime Hours',
            'field_trainings_completed': 'Trainings Completed',
            'field_training_hours': 'Training Hours',
            'field_certifications': 'Certifications',
            'field_manager': 'Manager',
            'field_location': 'Location',
            'field_employment_type': 'Employment Type',
            'field_status': 'Status',
            
            # Analysis Button
            'analyze_button': '🚀 Proceed to Analysis',
            
            # Analysis Results
            'analysis_title': '📊 Step 3: Smart Data Analysis',
            'kpis_title': '📈 Key Results',
            'charts_title': '📊 Automatic Charts',
            'advanced_title': '🔍 Advanced Analysis',
            'correlations_title': 'Variable Correlations',
            'outliers_title': 'Outlier Detection',
            'outliers_found': 'Found {} outliers in salaries',
            'no_outliers': '✅ No outliers detected in salaries',
            'zero_std': 'Salary standard deviation is zero, cannot detect outliers',
            
            # Export
            'export_data': '📥 Download Modified Data (CSV)',
            'export_report': '📄 Download Full Report',
            'download_csv': '⬇️ Click to Download',
            'download_report': '⬇️ Click to Download',
            
            # Other Messages
            'loading': 'Loading...',
            'not_available': 'Not Available',
        }
    }
    
    @staticmethod
    def get_translation(key, language='ar'):
        """الحصول على ترجمة المفتاح باللغة المطلوبة"""
        lang_data = TranslationSystem.translations.get(language, TranslationSystem.translations['ar'])
        return lang_data.get(key, key)
    
    @staticmethod
    def translate(key):
        """ترجمة المفتاح بناءً على اللغة الحالية"""
        language = st.session_state.get('language', 'ar')
        return TranslationSystem.get_translation(key, language)

# تهيئة نظام الترجمة
translator = TranslationSystem()

# تحميل CSS مع دعم متعدد اللغات
def load_css(language='ar'):
    """تحميل CSS مع دعم اتجاه النص"""
    text_align = 'right' if language == 'ar' else 'left'
    font_family = "'Cairo', 'Segoe UI', Tahoma, sans-serif" if language == 'ar' else "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    
    css = f"""
    <style>
    .main-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        font-family: {font_family};
    }}
    
    .kpi-card {{
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.3s ease;
        font-family: {font_family};
        direction: {'rtl' if language == 'ar' else 'ltr'};
    }}
    
    .kpi-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }}
    
    .upload-box {{
        border: 2px dashed #4c51bf;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        background: #f7fafc;
        margin: 20px 0;
        font-family: {font_family};
        direction: {'rtl' if language == 'ar' else 'ltr'};
    }}
    
    .column-map-item {{
        background: #edf2f7;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-family: {font_family};
        direction: {'rtl' if language == 'ar' else 'ltr'};
    }}
    
    .warning-box {{
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        font-family: {font_family};
        direction: {'rtl' if language == 'ar' else 'ltr'};
    }}
    
    /* دعم النصوص العربية */
    .arabic-text {{
        font-family: 'Cairo', 'Segoe UI', sans-serif;
        direction: rtl;
        text-align: right;
    }}
    
    .english-text {{
        font-family: 'Segoe UI', Tahoma, sans-serif;
        direction: ltr;
        text-align: left;
    }}
    
    /* تنسيق عام للصفحة */
    .stApp {{
        font-family: {font_family};
        text-align: {text_align};
    }}
    </style>
    
    <!-- تحميل خط Cairo للعربية -->
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    """
    st.markdown(css, unsafe_allow_html=True)

# تهيئة حالة الجلسة
if 'language' not in st.session_state:
    st.session_state.language = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'column_mapping' not in st.session_state:
    st.session_state.column_mapping = {}
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# وظائف تبديل اللغة والمظهر
def toggle_language():
    st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'
    st.rerun()

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    st.rerun()

# تحميل CSS بناءً على اللغة
load_css(st.session_state.language)

# ==================== الشريط الجانبي ====================
with st.sidebar:
    st.markdown(f"### {translator.translate('sidebar_settings')}")
    
    # تبديل اللغة
    current_lang = 'العربية' if st.session_state.language == 'en' else 'English'
    lang_button = st.button(f"🌐 {current_lang}", use_container_width=True)
    if lang_button:
        toggle_language()
    
    # تبديل المظهر
    current_theme = '🌙 مظلم' if st.session_state.theme == 'light' else '☀️ فاتح'
    theme_button = st.button(current_theme, use_container_width=True)
    if theme_button:
        toggle_theme()
    
    st.divider()
    
    # تحميل الإعدادات السابقة
    if st.button(translator.translate('sidebar_load_settings'), use_container_width=True):
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                st.session_state.column_mapping = config.get('column_mapping', {})
                st.success(translator.translate('sidebar_load_success'))
        else:
            st.warning(translator.translate('sidebar_no_settings'))
    
    # حفظ الإعدادات
    if st.session_state.column_mapping:
        if st.button(translator.translate('sidebar_save_settings'), use_container_width=True):
            config = {
                'column_mapping': st.session_state.column_mapping,
                'saved_at': datetime.now().isoformat(),
                'language': st.session_state.language,
                'theme': st.session_state.theme
            }
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            st.success(translator.translate('sidebar_save_success'))

# ==================== العنوان الرئيسي ====================
st.markdown(f"""
<div class="main-header">
    <h1>{translator.translate('main_title')}</h1>
    <p>{translator.translate('main_subtitle')}</p>
</div>
""", unsafe_allow_html=True)

# ==================== الصفحة الرئيسية - تحميل الملف ====================
st.markdown(f"## {translator.translate('upload_title')}")

uploaded_file = st.file_uploader(
    translator.translate('upload_placeholder'),
    type=['xlsx', 'xls', 'csv'],
    help=translator.translate('upload_help')
)

if uploaded_file is not None:
    try:
        # تحميل الملف باستخدام المنظم الذكي
        loader = SmartFileLoader(uploaded_file)
        df = loader.load_file()
        st.session_state.df = df
        st.session_state.file_uploaded = True
        
        st.success(f"{translator.translate('upload_success')} ({len(df)} {translator.translate('stats_records')}، {len(df.columns)} {translator.translate('stats_columns')})")
        
        # عرض عينة من البيانات
        with st.expander(translator.translate('preview_data')):
            st.dataframe(df.head(), use_container_width=True)
        
        # عرض معلومات الأعمدة
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(translator.translate('stats_records'), len(df))
        with col2:
            st.metric(translator.translate('stats_columns'), len(df.columns))
        with col3:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            st.metric(translator.translate('stats_numeric'), len(numeric_cols))
        
    except Exception as e:
        st.error(f"{translator.translate('upload_error')} {str(e)}")

# ==================== تعيين الأعمدة ====================
if st.session_state.file_uploaded and st.session_state.df is not None:
    st.markdown(f"## {translator.translate('mapping_title')}")
    
    df = st.session_state.df
    columns = df.columns.tolist()
    
    # التعرف التلقائي على الأعمدة
    mapper = AutoColumnMapper(df)
    auto_suggestions = mapper.auto_detect_columns()
    
    st.markdown(translator.translate('mapping_auto'), unsafe_allow_html=True)
    
    # إنشاء تخطيط تعيين الأعمدة
    column_mapping = {}
    
    # عرض تعيين الأعمدة لكل فئة
    categories = {
        translator.translate('cat_employee_info'): ["employee_name", "employee_id", "department", "position", "hire_date"],
        translator.translate('cat_financial'): ["salary", "allowances", "bonus", "tax"],
        translator.translate('cat_performance'): ["performance_score", "kpi", "rating", "review_date"],
        translator.translate('cat_attendance'): ["attendance_days", "absent_days", "late_days", "overtime_hours"],
        translator.translate('cat_training'): ["trainings_completed", "training_hours", "certifications"],
        translator.translate('cat_management'): ["manager", "location", "employment_type", "status"]
    }
    
    for category, fields in categories.items():
        st.markdown(f"### {category}")
        
        cols = st.columns(3)
        for idx, field in enumerate(fields):
            with cols[idx % 3]:
                # ترجمة اسم الحقل للعرض
                field_display = translator.translate(f'field_{field}')
                
                # اقتراح تلقائي إن وجد
                suggested_column = auto_suggestions.get(field, translator.translate('not_available'))
                
                # إنشاء selectbox
                options = [f"❌ {translator.translate('not_available')}"] + columns
                default_idx = 0
                if suggested_column in columns:
                    default_idx = columns.index(suggested_column) + 1
                
                selected = st.selectbox(
                    f"**{field_display}**",
                    options=options,
                    index=default_idx,
                    key=f"map_{field}_{st.session_state.language}"
                )
                
                if selected != f"❌ {translator.translate('not_available')}":
                    column_mapping[field] = selected
    
    st.session_state.column_mapping = column_mapping
    
    # زر للمتابعة للتحليل
    if st.button(translator.translate('analyze_button'), type="primary", use_container_width=True):
        st.session_state.analysis_ready = True
        st.rerun()

# ==================== التحليل الذكي ====================
if st.session_state.get('analysis_ready', False):
    st.markdown(f"## {translator.translate('analysis_title')}")
    
    analyzer = FlexibleDataAnalyzer(
        st.session_state.df, 
        st.session_state.column_mapping
    )
    
    # التحليل الذكي للبيانات
    analysis = analyzer.analyze_all()
    st.session_state.analysis_results = analysis
    
    # عرض النتائج الرئيسية
    st.markdown(f"### {translator.translate('kpis_title')}")
    
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
    st.markdown(f"### {translator.translate('charts_title')}")
    
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
    with st.expander(translator.translate('advanced_title')):
        st.markdown(f"### {translator.translate('advanced_title')}")
        
        # تحليل العلاقات
        numeric_cols = []
        for col in st.session_state.df.columns:
            if pd.api.types.is_numeric_dtype(st.session_state.df[col]):
                numeric_cols.append(col)
        
        if len(numeric_cols) >= 2:
            st.markdown(f"#### {translator.translate('correlations_title')}")
            
            # خريطة حرارية للعلاقات
            numeric_df = st.session_state.df[numeric_cols]
            corr_matrix = numeric_df.corr()
            
            import plotly.express as px
            fig = px.imshow(
                corr_matrix,
                text_auto='.2f',
                color_continuous_scale='RdBu',
                aspect="auto",
                title=translator.translate('correlations_title')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # اكتشاف القيم الشاذة
        st.markdown(f"#### {translator.translate('outliers_title')}")
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
                                st.warning(translator.translate('outliers_found').format(len(outliers)))
                                st.dataframe(outliers[[salary_col]], use_container_width=True)
                            else:
                                st.success(translator.translate('no_outliers'))
                        else:
                            st.info(translator.translate('zero_std'))
                except Exception as e:
                    st.error(f"Error in outlier detection: {str(e)}")
    
    # تحميل التقارير
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # تصدير البيانات المعدلة
        if st.button(translator.translate('export_data'), use_container_width=True):
            modified_df = analyzer.get_modified_dataframe()
            csv = modified_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=translator.translate('download_csv'),
                data=csv,
                file_name="hr_data_modified.csv",
                mime="text/csv"
            )
    
    with col2:
        # تصدير التقرير
        if st.button(translator.translate('export_report'), use_container_width=True):
            report = analyzer.generate_report()
            st.download_button(
                label=translator.translate('download_report'),
                data=report,
                file_name="hr_analysis_report.txt",
                mime="text/plain"
            )