"""
وحدة التعرف التلقائي على الأعمدة وتخمين نوعها
نسخة معدّلة: دقة أعلى في اكتشاف التواريخ ونظام درجات للمطابقة
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

class AutoColumnMapper:
    def __init__(self, dataframe):
        self.df = dataframe
        self.column_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self):
        """تهيئة الأنماط للتعرف على الأعمدة"""
        return {
            'employee_name': {
                'patterns': ['name', 'employee.*name', 'full.*name', 'الاسم', r'\bname\b', r'\bnombre\b'],
                'keywords': ['name', 'nom', 'nombre', 'اسم']
            },
            'employee_id': {
                'patterns': ['\\bid\\b', 'employee.*id', 'emp.*id', 'رقم', 'معرف', 'كود'],
                'keywords': ['id', 'code', 'رقم', 'معرف']
            },
            'department': {
                'patterns': ['department', 'dept', 'division', 'unit', 'قسم', 'إدارة'],
                'keywords': ['dept', 'division', 'قسم', 'إدارة']
            },
            'salary': {
                'patterns': ['salary', 'pay', 'wage', 'income', 'راتب', 'أجر'],
                'keywords': ['salary', 'pay', 'راتب', 'أجر']
            },
            'hire_date': {
                'patterns': ['hire.*date', 'start.*date', 'join.*date', 'تاريخ', 'تعيين'],
                'keywords': ['date', 'تاريخ', 'join', 'start']
            },
            'performance_score': {
                'patterns': ['performance', 'rating', 'score', 'evaluation', 'أداء', 'تقييم'],
                'keywords': ['perf', 'rating', 'score', 'أداء', 'تقييم']
            },
            'position': {
                'patterns': ['position', 'job.*title', 'role', 'title', 'منصب', 'وظيفة'],
                'keywords': ['position', 'title', 'role', 'منصب']
            },
            'location': {
                'patterns': ['location', 'city', 'branch', 'موقع', 'فرع'],
                'keywords': ['location', 'city', 'موقع', 'فرع']
            },
            'status': {
                'patterns': ['status', 'state', 'condition', 'حالة', 'وضع'],
                'keywords': ['status', 'state', 'حالة']
            }
        }
    
    def auto_detect_columns(self):
        """التعرف التلقائي على أنواع الأعمدة"""
        suggestions = {}
        columns = self.df.columns.tolist()
        
        # نطبّق نظام درجات: كل تطابق يعطي نقاطًا ونأخذ الأعلى
        for col in columns:
            col_lower = str(col).lower()
            scores = {}
            
            for field_type, patterns_info in self.column_patterns.items():
                score = 0
                # أنماط regex (أولوية أعلى)
                for pattern in patterns_info['patterns']:
                    try:
                        if re.search(pattern, col_lower, re.IGNORECASE):
                            score += 3
                    except re.error:
                        # تجاهل أي نمط غير صالح
                        pass
                
                # كلمات مفتاحية
                for keyword in patterns_info['keywords']:
                    if keyword.lower() in col_lower:
                        score += 1
                
                # طول التطابق (تفضيل أسماء أقصر وأكثر تحديداً)
                scores[field_type] = score
            
            # اختر الحقل ذا أعلى درجة بشرط أن الدرجة ليست صفراً
            best_field = max(scores, key=lambda k: scores[k])
            if scores[best_field] > 0:
                # إذا الحقل لم يُقترح بعد، اعطه الاقتراح، أما إذا كان يوجد اقتراح مسبق فنتحقق من التعادل
                if best_field not in suggestions:
                    suggestions[best_field] = col
                else:
                    # إذا كان هناك اقتراح سابق، نحتفظ بالأقوى عبر مقارنة درجات العمود السابق/الحالي
                    # (هذه خطوة بسيطة؛ يمكن تحسينها لاحقًا)
                    pass
        
        # الآن نبحث عن أعمدة التواريخ بدقة أكبر
        for col in columns:
            if self._is_date_column(col):
                # نحاول تعيين hire_date أولاً إذا لم يكن موجودًا
                if 'hire_date' not in suggestions:
                    suggestions['hire_date'] = col
                elif 'review_date' not in suggestions:
                    suggestions['review_date'] = col
        
        return suggestions
    
    def _is_date_column(self, column_name):
        """فحص إذا كان العمود يحتوي على تواريخ بدقة أعلى"""
        if column_name not in self.df.columns:
            return False
        
        column_sample = self.df[column_name].dropna().astype(str).head(10)
        
        if len(column_sample) == 0:
            return False
        
        # إذا كان النوع بالفعل datetime
        if pd.api.types.is_datetime64_any_dtype(self.df[column_name]):
            return True
        
        # تجربة صيغ محددة (نستخدم raise لاكتشاف الصيغ بدقة)
        date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]
        success = False
        for fmt in date_formats:
            try:
                pd.to_datetime(column_sample, format=fmt, errors='raise')
                success = True
                break
            except Exception:
                continue
        
        if success:
            return True
        
        # كقاعدة أخيرة: إذا أكثر من %70 من القيم تحتوي على أرقام وشرطات أو شرطات مائلة كدلائل للتاريخ
        pattern_like_date = column_sample.str.match(r'^[0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4}$')
        if pattern_like_date.mean() > 0.7:
            return True
        
        return False
    
    def suggest_column_types(self):
        """اقتراح أنواع البيانات للأعمدة"""
        column_types = {}
        
        for column in self.df.columns:
            dtype = str(self.df[column].dtype)
            
            # فحص النوع
            if pd.api.types.is_numeric_dtype(self.df[column]):
                column_types[column] = 'numeric'
            elif pd.api.types.is_datetime64_any_dtype(self.df[column]):
                column_types[column] = 'date'
            elif self._is_categorical_column(column):
                column_types[column] = 'categorical'
            else:
                column_types[column] = 'text'
        
        return column_types
    
    def _is_categorical_column(self, column_name, max_unique_ratio=0.3):
        """فحص إذا كان العمود فئوي"""
        unique_count = self.df[column_name].nunique()
        total_count = len(self.df[column_name].dropna())
        
        if total_count == 0:
            return False
        
        unique_ratio = unique_count / total_count
        return unique_ratio <= max_unique_ratio and unique_count < 50