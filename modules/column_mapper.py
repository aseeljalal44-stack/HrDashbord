"""
وحدة التعرف التلقائي على الأعمدة وتخمين نوعها
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
                'patterns': ['name', 'employee.*name', 'full.*name', 'الاسم', 'اسم', 'موظف'],
                'keywords': ['name', 'nom', 'nombre', 'اسم']
            },
            'employee_id': {
                'patterns': ['id', 'employee.*id', 'emp.*id', 'رقم', 'معرف', 'كود'],
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
        
        for column in columns:
            column_lower = str(column).lower()
            
            # البحث عن تطابقات في الأنماط
            for field_type, patterns_info in self.column_patterns.items():
                # البحث في الأنماط
                for pattern in patterns_info['patterns']:
                    if re.search(pattern, column_lower, re.IGNORECASE):
                        suggestions[field_type] = column
                        break
                
                # البحث في الكلمات المفتاحية
                if field_type not in suggestions:
                    for keyword in patterns_info['keywords']:
                        if keyword.lower() in column_lower:
                            suggestions[field_type] = column
                            break
            
            # محاولة التعرف على التواريخ
            if self._is_date_column(column):
                if 'hire_date' not in suggestions:
                    suggestions['hire_date'] = column
                elif 'review_date' not in suggestions:
                    suggestions['review_date'] = column
        
        return suggestions
    
    def _is_date_column(self, column_name):
        """فحص إذا كان العمود يحتوي على تواريخ"""
        if column_name not in self.df.columns:
            return False
        
        column_sample = self.df[column_name].dropna().head(10)
        
        if len(column_sample) == 0:
            return False
        
        # محاولة التحويل إلى تاريخ
        try:
            # إذا كان النوع بالفعل datetime
            if pd.api.types.is_datetime64_any_dtype(self.df[column_name]):
                return True
            
            # اختبار التحويل
            test_dates = pd.to_datetime(column_sample, errors='coerce')
            success_rate = test_dates.notna().sum() / len(column_sample)
            
            return success_rate > 0.7  # إذا نجح في 70% من الحالات
        except:
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