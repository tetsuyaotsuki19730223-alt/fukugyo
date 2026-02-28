from django import forms

class DiagnosisForm(forms.Form):
    Q1 = [("employee", "会社員"), ("freelance", "フリーランス志望"), ("unemployed", "無職・転職中"), ("side", "副業経験あり")]
    Q2 = [("lt30", "1日30分未満"), ("h1", "1時間"), ("h2", "2時間以上"), ("weekend", "休日まとめて")]
    Q3 = [("make", "作る（制作/開発）"), ("post", "発信（文章/動画）"), ("resell", "仕入れ/リサーチ"), ("analyze", "分析/改善")]
    Q4 = [("low", "低い（安定重視）"), ("mid", "少しOK"), ("high", "攻めたい"), ("very", "全然OK")]
    Q5 = [("1", "月1万"), ("5", "月5万"), ("10", "月10万"), ("indep", "独立")]

    q1_status = forms.ChoiceField(choices=Q1, widget=forms.RadioSelect)
    q2_time = forms.ChoiceField(choices=Q2, widget=forms.RadioSelect)
    q3_strength = forms.ChoiceField(choices=Q3, widget=forms.RadioSelect)
    q4_risk = forms.ChoiceField(choices=Q4, widget=forms.RadioSelect)
    q5_goal = forms.ChoiceField(choices=Q5, widget=forms.RadioSelect)