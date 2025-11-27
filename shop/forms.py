from django import forms
from .models import CustomUser, StudentAnswer, Question, Exam, StudyMaterial, Topic
class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'occupation', 'school', 'gender']
        
        
class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'subject', 'created_by']
        
        
class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['topic', 'title', 'file']

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
  
