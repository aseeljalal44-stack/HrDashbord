"""
وحدة تحميل الملفات الذكية - تدعم جميع تنسيقات Excel و CSV
"""

import pandas as pd
import numpy as np
import io
from datetime import datetime

class SmartFileLoader:
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.file_extension = None
        self.sheet_names = []
        
    def load_file(self):
        """تحميل الملف بتنسيقاته المختلفة"""
        
        # تحديد نوع الملف
        file_name = self.uploaded_file.name.lower()
        
        if file_name.endswith('.csv'):
            self.file_extension = 'csv'
            return self._load_csv()
        elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            self.file_extension = 'excel'
            return self._load_excel()
        else:
            raise ValueError("نوع الملف غير مدعوم. الرجاء استخدام Excel (.xlsx, .xls) أو CSV")
    
    def _load_csv(self):
        """تحميل ملف CSV مع اكتشاف الترميز تلقائياً"""
        # قراءة الملف كـ bytes
        content = self.uploaded_file.getvalue()
        
        # محاولة ترميزات مختلفة
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1256', 'windows-1256']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(
                    io.StringIO(content.decode(encoding)),
                    encoding=encoding
                )
                return df
            except UnicodeDecodeError:
                continue
        
        raise ValueError("تعذر قراءة الملف. الرجاء التحقق من الترميز")
    
    def _load_excel(self):
        """تحميل ملف Excel مع جميع الأوراق"""
        # قراءة أسماء الأوراق أولاً
        xls = pd.ExcelFile(self.uploaded_file)
        self.sheet_names = xls.sheet_names
        
        # محاولة تحميل الورقة الأولى (الأكثر شيوعاً)
        try:
            # قراءة الورقة الأولى
            df = pd.read_excel(
                self.uploaded_file,
                sheet_name=0,
                dtype=str,  # قراءة كل شيء كـ نص أولاً
                na_values=['', 'NA', 'N/A', 'null', 'NULL']
            )
            
            # محاولة تحويل الأعمدة الرقمية
            df = self._convert_numeric_columns(df)
            
            return df
            
        except Exception as e:
            raise ValueError(f"خطأ في قراءة ملف Excel: {str(e)}")
    
    def _convert_numeric_columns(self, df):
        """محاولة تحويل الأعمدة إلى أنواع رقمية"""
        df_converted = df.copy()
        
        for column in df.columns:
            # محاولة التحويل إلى عدد
            try:
                # محاولة تحويل إلى عدد صحيح أولاً
                df_converted[column] = pd.to_numeric(df_converted[column], errors='ignore')
            except:
                pass
            
            # محاولة تحويل إلى تاريخ
            try:
                df_converted[column] = pd.to_datetime(df_converted[column], errors='ignore')
            except:
                pass
        
        return df_converted
    
    def get_file_info(self):
        """الحصول على معلومات الملف"""
        return {
            'filename': self.uploaded_file.name,
            'size': len(self.uploaded_file.getvalue()),
            'type': self.file_extension,
            'sheet_names': self.sheet_names
        }