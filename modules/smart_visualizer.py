"""
وحدة إنشاء الرسوم البيانية الذكية - تتكيف مع البيانات المتاحة
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class SmartVisualizer:
    def __init__(self, dataframe, column_mapping, analysis_results):
        self.df = dataframe
        self.mapping = column_mapping
        self.analysis = analysis_results
    
    def generate_all_charts(self):
        """توليد جميع الرسوم البيانية الممكنة"""
        charts = []
        
        # 1. توزيع الأقسام
        if 'department' in self.mapping:
            dept_chart = self._create_department_chart()
            if dept_chart:
                charts.append(dept_chart)
        
        # 2. توزيع الرواتب
        if 'salary' in self.mapping:
            salary_chart = self._create_salary_chart()
            if salary_chart:
                charts.append(salary_chart)
        
        # 3. توزيع الأداء
        if 'performance_score' in self.mapping:
            performance_chart = self._create_performance_chart()
            if performance_chart:
                charts.append(performance_chart)
        
        # 4. العلاقة بين الراتب والأداء
        if 'salary' in self.mapping and 'performance_score' in self.mapping:
            correlation_chart = self._create_correlation_chart()
            if correlation_chart:
                charts.append(correlation_chart)
        
        # 5. توزيع المواقع
        if 'location' in self.mapping:
            location_chart = self._create_location_chart()
            if location_chart:
                charts.append(location_chart)
        
        # 6. توزيع الوظائف
        if 'position' in self.mapping:
            position_chart = self._create_position_chart()
            if position_chart:
                charts.append(position_chart)
        
        return charts
    
    def _create_department_chart(self):
        """إنشاء رسم توزيع الأقسام"""
        dept_col = self.mapping['department']
        
        if dept_col not in self.df.columns:
            return None
        
        # حساب التوزيع
        dept_counts = self.df[dept_col].value_counts().reset_index()
        dept_counts.columns = ['department', 'count']
        
        # إذا كان هناك أكثر من 15 قسم، أخذ أول 15 فقط
        if len(dept_counts) > 15:
            dept_counts = dept_counts.head(15)
        
        # إنشاء الرسم
        fig = px.bar(
            dept_counts,
            x='department',
            y='count',
            color='count',
            color_continuous_scale='Blues',
            title='توزيع الموظفين حسب القسم'
        )
        
        fig.update_layout(
            xaxis_title='القسم',
            yaxis_title='عدد الموظفين',
            coloraxis_showscale=False,
            xaxis_tickangle=45
        )
        
        return {
            'title': 'توزيع الموظفين حسب القسم',
            'figure': fig,
            'available': True
        }
    
    def _create_salary_chart(self):
        """إنشاء رسم توزيع الرواتب"""
        salary_col = self.mapping['salary']
        
        if salary_col not in self.df.columns:
            return None
        
        try:
            # تحويل إلى عدد
            salary_data = pd.to_numeric(self.df[salary_col], errors='coerce').dropna()
            
            if len(salary_data) == 0:
                return None
            
            # إنشاء histogram
            fig = px.histogram(
                salary_data,
                nbins=30,
                title='توزيع الرواتب',
                labels={'value': 'الراتب', 'count': 'عدد الموظفين'}
            )
            
            # إضافة خط للمتوسط
            avg_salary = salary_data.mean()
            if not np.isnan(avg_salary):
                fig.add_vline(
                    x=avg_salary,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"المتوسط: ${avg_salary:,.0f}",
                    annotation_position="top right"
                )
            
            return {
                'title': 'توزيع الرواتب',
                'figure': fig,
                'available': True
            }
            
        except:
            return None
    
    def _create_performance_chart(self):
        """إنشاء رسم توزيع الأداء"""
        perf_col = self.mapping['performance_score']
        
        if perf_col not in self.df.columns:
            return None
        
        try:
            # تحويل إلى عدد
            perf_data = pd.to_numeric(self.df[perf_col], errors='coerce').dropna()
            
            if len(perf_data) == 0:
                return None
            
            # إنشاء box plot
            fig = px.box(
                perf_data,
                title='توزيع درجات الأداء',
                labels={'value': 'درجة الأداء'}
            )
            
            fig.update_layout(
                xaxis_title='الأداء',
                yaxis_title='درجة الأداء'
            )
            
            return {
                'title': 'توزيع درجات الأداء',
                'figure': fig,
                'available': True
            }
            
        except:
            return None
    
    def _create_correlation_chart(self):
        """إنشاء رسم العلاقة بين الراتب والأداء"""
        salary_col = self.mapping['salary']
        perf_col = self.mapping['performance_score']
        
        if salary_col not in self.df.columns or perf_col not in self.df.columns:
            return None
        
        try:
            # تحويل إلى عدد
            df_clean = self.df.copy()
            df_clean[salary_col] = pd.to_numeric(df_clean[salary_col], errors='coerce')
            df_clean[perf_col] = pd.to_numeric(df_clean[perf_col], errors='coerce')
            df_clean = df_clean.dropna(subset=[salary_col, perf_col])
            
            if len(df_clean) == 0:
                return None
            
            # إنشاء scatter plot
            fig = px.scatter(
                df_clean,
                x=perf_col,
                y=salary_col,
                trendline="ols",
                title='العلاقة بين الراتب والأداء',
                labels={perf_col: 'درجة الأداء', salary_col: 'الراتب'}
            )
            
            # حساب معامل الارتباط
            correlation = df_clean[[perf_col, salary_col]].corr().iloc[0,1]
            
            # إضافة نص معامل الارتباط
            if not np.isnan(correlation):
                fig.add_annotation(
                    x=0.05, y=0.95,
                    xref="paper", yref="paper",
                    text=f"معامل الارتباط: {correlation:.2f}",
                    showarrow=False,
                    bgcolor="white",
                    bordercolor="black",
                    borderwidth=1
                )
            
            return {
                'title': 'العلاقة بين الراتب والأداء',
                'figure': fig,
                'available': True
            }
            
        except:
            return None
    
    def _create_location_chart(self):
        """إنشاء رسم توزيع المواقع"""
        location_col = self.mapping['location']
        
        if location_col not in self.df.columns:
            return None
        
        # حساب التوزيع
        location_counts = self.df[location_col].value_counts().reset_index()
        location_counts.columns = ['location', 'count']
        
        # إذا كان هناك أكثر من 10 مواقع، أخذ أول 10 فقط
        if len(location_counts) > 10:
            location_counts = location_counts.head(10)
        
        # إنشاء pie chart
        fig = px.pie(
            location_counts,
            values='count',
            names='location',
            title='توزيع الموظفين حسب الموقع',
            hole=0.4
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return {
            'title': 'توزيع الموظفين حسب الموقع',
            'figure': fig,
            'available': True
        }
    
    def _create_position_chart(self):
        """إنشاء رسم توزيع الوظائف"""
        position_col = self.mapping['position']
        
        if position_col not in self.df.columns:
            return None
        
        # حساب التوزيع
        position_counts = self.df[position_col].value_counts().reset_index()
        position_counts.columns = ['position', 'count']
        
        # إذا كان هناك أكثر من 15 وظيفة، أخذ أول 15 فقط
        if len(position_counts) > 15:
            position_counts = position_counts.head(15)
        
        # إنشاء horizontal bar chart
        fig = px.bar(
            position_counts,
            y='position',
            x='count',
            orientation='h',
            color='count',
            color_continuous_scale='Viridis',
            title='توزيع الموظفين حسب المسمى الوظيفي'
        )
        
        fig.update_layout(
            yaxis_title='المسمى الوظيفي',
            xaxis_title='عدد الموظفين',
            coloraxis_showscale=False
        )
        
        return {
            'title': 'توزيع الموظفين حسب المسمى الوظيفي',
            'figure': fig,
            'available': True
        }