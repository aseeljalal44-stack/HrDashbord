"""
وحدة التحليل الذكي للبيانات - تعمل مع أي هيكل بيانات
الإصدار مع إصلاح الأخطاء
"""

import pandas as pd
import numpy as np
from datetime import datetime

class FlexibleDataAnalyzer:
    def __init__(self, dataframe, column_mapping):
        self.df = dataframe.copy()
        self.mapping = column_mapping
        self.reverse_mapping = {v: k for k, v in column_mapping.items() if v != "❌ لا يوجد"}
    
    def analyze_all(self):
        """إجراء جميع التحليلات المتاحة"""
        analysis_results = {
            'kpis': {},
            'distributions': {},
            'correlations': {},
            'insights': [],
            'warnings': []
        }
        
        # 1. تحليل KPIs
        analysis_results['kpis'] = self._calculate_kpis()
        
        # 2. توزيع البيانات
        analysis_results['distributions'] = self._analyze_distributions()
        
        # 3. اكتشاف العلاقات
        analysis_results['correlations'] = self._find_correlations()
        
        # 4. استخلاص Insights
        analysis_results['insights'] = self._extract_insights()
        
        # 5. التحذيرات
        analysis_results['warnings'] = self._check_data_quality()
        
        return analysis_results
    
    def _calculate_kpis(self):
        """حساب المؤشرات الرئيسية بناءً على البيانات المتاحة"""
        kpis = {}
        
        # إجمالي الموظفين (دائماً موجود)
        total_employees = len(self.df)
        kpis['total_employees'] = {
            'value': f"{total_employees:,}",
            'label': 'إجمالي الموظفين',
            'icon': '👥'
        }
        
        # التحقق من وجود رواتب
        if 'salary' in self.mapping:
            salary_col = self.mapping['salary']
            if salary_col in self.df.columns:
                try:
                    # تحويل إلى عدد إذا لزم الأمر
                    if not pd.api.types.is_numeric_dtype(self.df[salary_col]):
                        self.df[salary_col] = pd.to_numeric(self.df[salary_col], errors='coerce')
                    
                    salary_data = self.df[salary_col].dropna()
                    if len(salary_data) > 0:
                        avg_salary = salary_data.mean()
                        median_salary = salary_data.median()
                        
                        kpis['avg_salary'] = {
                            'value': f"${avg_salary:,.0f}" if not np.isnan(avg_salary) else "N/A",
                            'label': 'متوسط الراتب',
                            'icon': '💰'
                        }
                        
                        kpis['median_salary'] = {
                            'value': f"${median_salary:,.0f}" if not np.isnan(median_salary) else "N/A",
                            'label': 'الراتب الوسيط',
                            'icon': '📊'
                        }
                except Exception as e:
                    kpis['salary_error'] = {
                        'value': 'خطأ في الحساب',
                        'label': 'متوسط الراتب',
                        'icon': '⚠️'
                    }
        
        # التحقق من وجود أقسام
        if 'department' in self.mapping:
            dept_col = self.mapping['department']
            if dept_col in self.df.columns:
                dept_count = self.df[dept_col].nunique()
                kpis['departments'] = {
                    'value': dept_count,
                    'label': 'عدد الأقسام',
                    'icon': '🏢'
                }
        
        # التحقق من وجود أداء
        if 'performance_score' in self.mapping:
            perf_col = self.mapping['performance_score']
            if perf_col in self.df.columns:
                try:
                    if not pd.api.types.is_numeric_dtype(self.df[perf_col]):
                        self.df[perf_col] = pd.to_numeric(self.df[perf_col], errors='coerce')
                    
                    perf_data = self.df[perf_col].dropna()
                    if len(perf_data) > 0:
                        avg_perf = perf_data.mean()
                        kpis['avg_performance'] = {
                            'value': f"{avg_perf:.1f}/5" if not np.isnan(avg_perf) else "N/A",
                            'label': 'متوسط الأداء',
                            'icon': '📈'
                        }
                except:
                    pass
        
        # التحقق من وجود تواريخ تعيين
        if 'hire_date' in self.mapping:
            date_col = self.mapping['hire_date']
            if date_col in self.df.columns:
                try:
                    # حساب العمر التنظيمي
                    if not pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
                        self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
                    
                    current_date = pd.Timestamp.now()
                    tenure_days = (current_date - self.df[date_col]).dt.days
                    avg_tenure = tenure_days.mean() / 365.25
                    
                    if not np.isnan(avg_tenure):
                        kpis['avg_tenure'] = {
                            'value': f"{avg_tenure:.1f} سنوات",
                            'label': 'متوسط العمر التنظيمي',
                            'icon': '⏳'
                        }
                except:
                    pass
        
        return kpis
    
    def _analyze_distributions(self):
        """تحليل توزيع البيانات"""
        distributions = {}
        
        # توزيع الأقسام
        if 'department' in self.mapping:
            dept_col = self.mapping['department']
            if dept_col in self.df.columns:
                dept_dist = self.df[dept_col].value_counts().to_dict()
                distributions['department'] = dept_dist
        
        # توزيع المواقع
        if 'location' in self.mapping:
            loc_col = self.mapping['location']
            if loc_col in self.df.columns:
                loc_dist = self.df[loc_col].value_counts().to_dict()
                distributions['location'] = loc_dist
        
        # توزيع الوظائف
        if 'position' in self.mapping:
            pos_col = self.mapping['position']
            if pos_col in self.df.columns:
                pos_dist = self.df[pos_col].value_counts().head(10).to_dict()
                distributions['position'] = pos_dist
        
        # توزيع الرواتب
        if 'salary' in self.mapping:
            salary_col = self.mapping['salary']
            if salary_col in self.df.columns:
                try:
                    salary_data = pd.to_numeric(self.df[salary_col], errors='coerce').dropna()
                    if len(salary_data) > 0:
                        distributions['salary'] = {
                            'min': float(salary_data.min()),
                            'max': float(salary_data.max()),
                            'mean': float(salary_data.mean()),
                            'median': float(salary_data.median()),
                            'std': float(salary_data.std())
                        }
                except:
                    pass
        
        return distributions
    
    def _find_correlations(self):
        """اكتشاف العلاقات بين المتغيرات"""
        correlations = {}
        
        # العثور على الأعمدة الرقمية
        numeric_cols = []
        for field_type, col_name in self.mapping.items():
            if col_name in self.df.columns:
                try:
                    # محاولة تحويل إلى عدد
                    numeric_series = pd.to_numeric(self.df[col_name], errors='coerce')
                    if numeric_series.notna().sum() > 0:  # إذا كان هناك أرقام
                        numeric_cols.append(col_name)
                        self.df[col_name] = numeric_series
                except:
                    continue
        
        # حساب العلاقات إذا كان هناك أكثر من عمود رقمي
        if len(numeric_cols) >= 2:
            try:
                corr_matrix = self.df[numeric_cols].corr()
                correlations['matrix'] = corr_matrix.to_dict()
                
                # العثور على أقوى العلاقات
                strong_correlations = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_value = corr_matrix.iloc[i, j]
                        if not pd.isna(corr_value) and abs(corr_value) > 0.5:
                            strong_correlations.append({
                                'col1': corr_matrix.columns[i],
                                'col2': corr_matrix.columns[j],
                                'correlation': corr_value
                            })
                
                correlations['strong'] = strong_correlations
            except:
                pass
        
        return correlations
    
    def _extract_insights(self):
        """استخلاص رؤى من البيانات"""
        insights = []
        
        # 1. إذا كان هناك أقسام
        if 'department' in self.mapping and 'salary' in self.mapping:
            dept_col = self.mapping['department']
            salary_col = self.mapping['salary']
            
            if dept_col in self.df.columns and salary_col in self.df.columns:
                try:
                    self.df[salary_col] = pd.to_numeric(self.df[salary_col], errors='coerce')
                    dept_salary = self.df.groupby(dept_col)[salary_col].mean().sort_values()
                    
                    if len(dept_salary) > 0:
                        highest_dept = dept_salary.idxmax()
                        lowest_dept = dept_salary.idxmin()
                        
                        insights.append(f"أعلى راتب في قسم: **{highest_dept}**")
                        insights.append(f"أقل راتب في قسم: **{lowest_dept}**")
                except:
                    pass
        
        # 2. إذا كان هناك أداء ورواتب
        if 'performance_score' in self.mapping and 'salary' in self.mapping:
            perf_col = self.mapping['performance_score']
            salary_col = self.mapping['salary']
            
            if perf_col in self.df.columns and salary_col in self.df.columns:
                try:
                    self.df[perf_col] = pd.to_numeric(self.df[perf_col], errors='coerce')
                    self.df[salary_col] = pd.to_numeric(self.df[salary_col], errors='coerce')
                    
                    # حساب الارتباط باستخدام numpy
                    valid_data = self.df[[perf_col, salary_col]].dropna()
                    if len(valid_data) > 1:
                        correlation = np.corrcoef(valid_data[perf_col], valid_data[salary_col])[0, 1]
                        
                        if not np.isnan(correlation):
                            if correlation > 0.5:
                                insights.append("📈 العلاقة بين الأداء والراتب **إيجابية وقوية**")
                            elif correlation > 0.3:
                                insights.append("📈 العلاقة بين الأداء والراتب **إيجابية**")
                            elif correlation < -0.3:
                                insights.append("📉 العلاقة بين الأداء والراتب **سلبية**")
                            else:
                                insights.append("⚖️ **لا توجد علاقة واضحة** بين الأداء والراتب")
                except:
                    pass
        
        # 3. توزيع الجنس (إذا وجد)
        gender_keywords = ['gender', 'sex', 'جنس', 'الجنس']
        for col in self.df.columns:
            if any(keyword in str(col).lower() for keyword in gender_keywords):
                if self.df[col].nunique() <= 5:  # عمود فئوي محتمل
                    gender_dist = self.df[col].value_counts()
                    for gender, count in gender_dist.items():
                        percentage = (count / len(self.df)) * 100
                        insights.append(f"**{gender}**: {percentage:.1f}% من الموظفين")
                    break
        
        return insights
    
    def _check_data_quality(self):
        """فحص جودة البيانات - إصدار مصحح"""
        warnings = []
        
        # 1. فحص القيم المفقودة
        missing_percentage = (self.df.isnull().sum() / len(self.df)) * 100
        high_missing = missing_percentage[missing_percentage > 20].index.tolist()
        
        if high_missing:
            warnings.append(f"⚠️ أعمدة بها قيم مفقودة >20%: {', '.join(high_missing[:5])}")
        
        # 2. فحص التكرارات
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            warnings.append(f"⚠️ يوجد {duplicates} سجل مكرر")
        
        # 3. فحص القيم المتطرفة في الرواتب - إصلاح المقارنة
        if 'salary' in self.mapping:
            salary_col = self.mapping['salary']
            if salary_col in self.df.columns:
                try:
                    # التحويل إلى عدد وفلترة القيم الناقصة
                    salary_data = pd.to_numeric(self.df[salary_col], errors='coerce')
                    salary_data = salary_data.dropna()
                    
                    if len(salary_data) > 0:
                        # التحقق من أن البيانات رقمية
                        if pd.api.types.is_numeric_dtype(salary_data):
                            # حساب القيم المتطرفة باستخدام IQR
                            q1 = salary_data.quantile(0.25)
                            q3 = salary_data.quantile(0.75)
                            iqr = q3 - q1
                            
                            if iqr > 0:  # تجنب iqr = 0
                                lower_bound = q1 - 1.5 * iqr
                                upper_bound = q3 + 1.5 * iqr
                                
                                # المقارنة مع bound (لاستخدام int)
                                outliers = salary_data[(salary_data < lower_bound) | (salary_data > upper_bound)]
                                
                                if len(outliers) > 0:
                                    warnings.append(f"⚠️ تم اكتشاف {len(outliers)} قيمة شاذة في الرواتب (استخدام IQR)")
                        else:
                            warnings.append("⚠️ عمود الراتب ليس بيانات رقمية (لا يمكن اكتشاف قيم شاذة)")
                except Exception as e:
                    warnings.append(f"⚠️ خطأ في اكتشاف القيم الشاذة: {str(e)[:50]}")
        
        # 4. فحص التواريخ غير المنطقية
        if 'hire_date' in self.mapping:
            date_col = self.mapping['hire_date']
            if date_col in self.df.columns:
                try:
                    dates = pd.to_datetime(self.df[date_col], errors='coerce')
                    future_dates = dates[dates > pd.Timestamp.now()]
                    if len(future_dates) > 0:
                        warnings.append(f"⚠️ يوجد {len(future_dates)} تاريخ تعيين في المستقبل")
                except:
                    pass
        
        # 5. تحذير عام إذا كان هناك تحليل غير مكتمل
        if len(self.df) < 10:
            warnings.append("⚠️ عدد السجلات قليل جداً، النتائج قد لا تكون دقيقة")
        
        return warnings
    
    def get_modified_dataframe(self):
        """الحصول على البيانات بعد التعديل"""
        return self.df
    
    def generate_report(self):
        """توليد تقرير نصي عن التحليل - إصدار محسن"""
        try:
            report_lines = []
            
            # العنوان الرئيسي
            report_lines.append("=" * 80)
            report_lines.append("تقرير تحليل بيانات الموارد البشرية")
            report_lines.append("=" * 80)
            report_lines.append(f"تاريخ التوليد: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            report_lines.append("-" * 80)
            report_lines.append("")
            
            # معلومات عامة
            report_lines.append("📋 معلومات عامة:")
            report_lines.append(f"   • عدد الموظفين: {len(self.df)}")
            report_lines.append(f"   • عدد الأعمدة: {len(self.df.columns)}")
            
            # الأعمدة الرئيسية المستخدمة
            used_columns = [v for v in self.mapping.values() if v not in ["❌ لا يوجد", "❌ غير متوفر"]]
            if used_columns:
                report_lines.append(f"   • الأعمدة المستخدمة: {len(used_columns)} من {len(self.df.columns)}")
            report_lines.append("")
            
            # KPIs
            kpis = self._calculate_kpis()
            report_lines.append("📊 المؤشرات الرئيسية (KPIs):")
            for kpi_name, kpi_info in kpis.items():
                value = kpi_info['value']
                label = kpi_info['label']
                icon = kpi_info.get('icon', '')
                report_lines.append(f"   {icon} {label}: {value}")
            report_lines.append("")
            
            # Insights
            insights = self._extract_insights()
            if insights:
                report_lines.append("💡 الرؤى المستخلصة:")
                for insight in insights:
                    report_lines.append(f"   • {insight}")
                report_lines.append("")
            
            # Warnings
            warnings = self._check_data_quality()
            if warnings:
                report_lines.append("⚠️ تحذيرات جودة البيانات:")
                for warning in warnings:
                    clean_warning = str(warning).replace('<', '').replace('>', '')
                    report_lines.append(f"   • {clean_warning}")
                report_lines.append("")
            
            # توزيع الأقسام
            if 'department' in self.mapping:
                dept_col = self.mapping['department']
                if dept_col in self.df.columns:
                    dept_counts = self.df[dept_col].value_counts()
                    if len(dept_counts) > 0:
                        report_lines.append("🏢 توزيع الموظفين حسب القسم:")
                        for dept, count in dept_counts.head(5).items():
                            percentage = (count / len(self.df)) * 100
                            report_lines.append(f"   • {dept}: {count} موظف ({percentage:.1f}%)")
                        report_lines.append("")
            
            # توزيع الرواتب
            if 'salary' in self.mapping:
                salary_col = self.mapping['salary']
                if salary_col in self.df.columns:
                    salary_data = pd.to_numeric(self.df[salary_col], errors='coerce').dropna()
                    if len(salary_data) > 0:
                        report_lines.append("💰 ملخص الرواتب:")
                        report_lines.append(f"   • أعلى راتب: ${salary_data.max():,.0f}")
                        report_lines.append(f"   • أقل راتب: ${salary_data.min():,.0f}")
                        report_lines.append(f"   • متوسط الراتب: ${salary_data.mean():,.0f}")
                        report_lines.append(f"   • الانحراف المعياري: ${salary_data.std():,.0f}")
                        report_lines.append("")
            
            # Recommendations
            report_lines.append("✅ التوصيات:")
            report_lines.append("   1. مراجعة هيكل الرواتب لضمان العدالة")
            report_lines.append("   2. ربط نظام المكافآت بالأداء")
            report_lines.append("   3. تحليل توزيع المواهب بين الأقسام")
            report_lines.append("   4. معالجة القيم المفقودة في البيانات")
            report_lines.append("   5. تحديث سياسات التوظيف بناءً على التحليل")
            report_lines.append("")
            
            # تذييل التقرير
            report_lines.append("=" * 80)
            report_lines.append("ملاحظات:")
            report_lines.append("   • هذا التقرير تم إنشاؤه تلقائياً بواسطة لوحة تحكم HR الذكية")
            report_lines.append("   • للاستفسارات: فريق تحليل البيانات - الموارد البشرية")
            report_lines.append("=" * 80)
            
            # إنشاء النص النهائي
            report_text = "\n".join(report_lines)
            
            # التحقق من الترميز الصحيح
            try:
                report_text = report_text.encode('utf-8').decode('utf-8')
            except:
                pass
            
            return report_text
            
        except Exception as e:
            error_report = f"""
============================================================
خطأ في إنشاء التقرير
============================================================
حدث خطأ أثناء إنشاء التقرير: {str(e)}

البيانات المتاحة:
- عدد الصفوف: {len(self.df)}
- عدد الأعمدة: {len(self.df.columns)}
- الأعمدة المعينة: {self.mapping}

يرجى التحقق من البيانات والمحاولة مرة أخرى.
============================================================
"""
            return error_report