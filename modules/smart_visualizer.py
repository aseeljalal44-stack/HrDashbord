########################################
# SmartVisualizer (Final Version)
########################################

import plotly.express as px
import pandas as pd
import numpy as np

class SmartVisualizer:
    def __init__(self, df, mapping, analysis):
        self.df = df
        self.mapping = mapping
        self.analysis = analysis

    def generate_all_charts(self):
        charts = []

        if "department" in self.mapping:
            charts.append(self._chart_department())

        if "salary" in self.mapping:
            charts.append(self._chart_salary())

        if "performance_score" in self.mapping:
            charts.append(self._chart_performance())

        return charts

    def _chart_department(self):
        col = self.mapping["department"]
        data = self.df[col].value_counts().reset_index()
        data.columns = ["department", "count"]

        fig = px.bar(data, x="department", y="count", title="توزيع الأقسام")

        return {"title": "توزيع الأقسام", "figure": fig}

    def _chart_salary(self):
        col = self.mapping["salary"]
        sal = pd.to_numeric(self.df[col], errors="coerce")

        fig = px.histogram(sal, nbins=30, title="توزيع الرواتب")

        return {"title": "توزيع الرواتب", "figure": fig}

    def _chart_performance(self):
        col = self.mapping["performance_score"]
        perf = pd.to_numeric(self.df[col], errors="coerce")

        fig = px.box(perf, title="توزيع الأداء")

        return {"title": "توزيع الأداء", "figure": fig}