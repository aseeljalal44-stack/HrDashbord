########################################
# FlexibleDataAnalyzer (Final Version)
########################################

import pandas as pd
import numpy as np
from datetime import datetime

class FlexibleDataAnalyzer:
    def __init__(self, dataframe, column_mapping):
        self.df = dataframe.copy()
        self.mapping = column_mapping

    ########################################
    # تحليل كامل
    ########################################
    def analyze_all(self):
        return {
            "kpis": self._calculate_kpis(),
            "distributions": self._analyze_distributions(),
            "correlations": self._find_correlations(),
            "insights": self._extract_insights(),
            "warnings": self._check_data_quality()
        }

    ########################################
    # KPIs
    ########################################
    def _calculate_kpis(self):
        k = {}

        # عدد الموظفين
        k["total_employees"] = {
            "value": len(self.df),
            "label": "إجمالي الموظفين",
            "icon": "👥",
        }

        # الرواتب
        if "salary" in self.mapping:
            col = self.mapping["salary"]
            salary = pd.to_numeric(self.df[col], errors="coerce")

            k["avg_salary"] = {
                "value": f"${salary.mean():,.0f}",
                "label": "متوسط الراتب",
                "icon": "💰",
            }

        # الأقسام
        if "department" in self.mapping:
            col = self.mapping["department"]

            k["departments"] = {
                "value": self.df[col].nunique(),
                "label": "عدد الأقسام",
                "icon": "🏢",
            }

        return k

    ########################################
    # التوزيعات
    ########################################
    def _analyze_distributions(self):
        d = {}

        if "department" in self.mapping:
            col = self.mapping["department"]
            d["department"] = self.df[col].value_counts().to_dict()

        if "location" in self.mapping:
            col = self.mapping["location"]
            d["location"] = self.df[col].value_counts().to_dict()

        if "position" in self.mapping:
            col = self.mapping["position"]
            d["position"] = self.df[col].value_counts().head(15).to_dict()

        return d

    ########################################
    # العلاقات
    ########################################
    def _find_correlations(self):
        corr = {}
        numeric_cols = []

        for key, col in self.mapping.items():
            if col in self.df:
                s = pd.to_numeric(self.df[col], errors="coerce")
                if s.notna().sum() > 10:
                    numeric_cols.append(col)
                    self.df[col] = s

        if len(numeric_cols) >= 2:
            c = self.df[numeric_cols].corr()
            corr["matrix"] = c.to_dict()

        return corr

    ########################################
    # Insights
    ########################################
    def _extract_insights(self):
        ins = []

        if "department" in self.mapping and "salary" in self.mapping:
            dept = self.mapping["department"]
            salary = pd.to_numeric(self.df[self.mapping["salary"]], errors="coerce")

            mean_by_dept = salary.groupby(self.df[dept]).mean().sort_values()
            ins.append(f"أعلى راتب: {mean_by_dept.index[-1]}")
            ins.append(f"أقل راتب: {mean_by_dept.index[0]}")

        return ins

    ########################################
    # جودة البيانات
    ########################################
    def _check_data_quality(self):
        warnings = []

        missing = self.df.isna().mean() * 100
        high = missing[missing > 20]

        if len(high):
            warnings.append(f"أعمدة بها قيم مفقودة: {', '.join(high.index)}")

        return warnings