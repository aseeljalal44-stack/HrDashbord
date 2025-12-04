"""
وحدة تحميل الملفات الذكية - تدعم جميع تنسيقات Excel و CSV
نسخة معدّلة: تحويل ذكي للأعمدة لتقليل التحذيرات والأخطاء
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
        
        last_err = None
        for encoding in encodings:
            try:
                # نفكّر مباشرة كنص، ونستخدم engine الافتراضي
                text = content.decode(encoding)
                df = pd.read_csv(io.StringIO(text))
                # نحاول تحويل الأعمدة بذكاء
                df = self._convert_columns_safely(df)
                return df
            except UnicodeDecodeError as e:
                last_err = e
                continue
            except Exception as e:
                # إذا فشل البارسر لسبب آخر، نحاول الاستمرار بالترميز التالي
                last_err = e
                continue
        
        raise ValueError("تعذر قراءة الملف. الرجاء التحقق من الترميز أو تنسيق الملف. الخطأ: {}".format(str(last_err)))
    
    def _load_excel(self):
        """تحميل ملف Excel مع جميع الأوراق"""
        # قراءة أسماء الأوراق أولاً
        xls = pd.ExcelFile(self.uploaded_file)
        self.sheet_names = xls.sheet_names
        
        # محاولة تحميل الورقة الأولى (الأكثر شيوعاً)
        try:
            # قراءة الورقة الأولى — لا نجبر dtype=str الآن
            df = pd.read_excel(
                self.uploaded_file,
                sheet_name=0,
                na_values=['', 'NA', 'N/A', 'null', 'NULL']
            )
            
            # تحويل الأعمدة بذكاء
            df = self._convert_columns_safely(df)
            
            return df
            
        except Exception as e:
            raise ValueError(f"خطأ في قراءة ملف Excel: {str(e)}")
    
    def _convert_columns_safely(self, df):
        """
        تحويل الأعمدة إلى أنواع مناسبة بطريقة آمنة:
        - نحاول تحويل الأعمدة الرقمية فقط إذا أظهرت العيّنة أنها رقمية بنسبة كافية
        - نحاول تحويل التواريخ فقط إذا نجحت مع أحد الصيغ الشائعة
        - لا نستخدم errors='ignore' لتفادي تحذيرات مستقبلية
        """
        df_converted = df.copy()
        
        for column in df.columns:
            try:
                col_series = df[column]
                non_null_sample = col_series.dropna().astype(str).head(20)
                if len(non_null_sample) == 0:
                    continue
                
                # 1) اختبار هل يبدو العمود رقمياً؟
                # نزيل الفواصل والأحرف الشائعة في الأرقام (مثل , و -) قبل الفحص
                sample_clean = non_null_sample.str.replace(r'[,\s]', '', regex=True)
                numeric_ratio = sample_clean.str.replace('.', '', 1).str.isnumeric().mean()
                
                if numeric_ratio >= 0.8:
                    # تحويل آمن إلى رقمي (coerce يحول غير القيم الرقمية إلى NaN)
                    df_converted[column] = pd.to_numeric(col_series, errors='coerce')
                    continue
                
                # 2) اختبار ما إذا كان العمود تاريخياً بصيغ شائعة
                date_formats = ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y")
                converted_to_date = False
                for fmt in date_formats:
                    try:
                        # نستخدم العينة لاختبار الصيغة بسرعة مع raise لتجنب التحذيرات
                        pd.to_datetime(non_null_sample, format=fmt, errors='raise')
                        # إذا نجح الاختبار، نطبق التحويل على العمود كاملاً
                        df_converted[column] = pd.to_datetime(col_series, format=fmt, errors='coerce')
                        converted_to_date = True
                        break
                    except Exception:
                        continue
                
                if converted_to_date:
                    continue
                
                # 3) إذا لم يتحول لرقم أو تاريخ: نتركه كما هو، لكن نؤدي تنظيف بسيط
                # إزالة مسافات زائدة
                if col_series.dtype == object:
                    df_converted[column] = col_series.astype(str).str.strip()
            
            except Exception:
                # حفاظاً على السلامة: إذا فشل أي شيء، لا نكسر التحميل
                df_converted[column] = df[column]
        
        return df_converted
    
    def get_file_info(self):
        """الحصول على معلومات الملف"""
        return {
            'filename': self.uploaded_file.name,
            'size': len(self.uploaded_file.getvalue()),
            'type': self.file_extension,
            'sheet_names': self.sheet_names
        }