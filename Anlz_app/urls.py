from django.urls import include, path

from .views import classroom, students, teachers

urlpatterns = [
    path('', classroom.home, name='home'),

    path('students/', include(([
        path('', students.QuizListView.as_view(), name='quiz_list'),
        path('interests/', students.StudentInterestsView.as_view(), name='student_interests'),
        path('taken/', students.TakenQuizListView.as_view(), name='taken_quiz_list'),
        path('quiz/<int:pk>/', students.take_quiz, name='take_quiz'),
        path('taken/<int:pk>/results/',students.view_results,name='results'),
        path('taken/<int:pk>/results/charts/',students.results_graph,name='charts'),
    ], 'classroom'), namespace='students')),

    path('teachers/', include(([
        path('', teachers.QuizListView.as_view(), name='quiz_change_list'),
        path('students/activate',teachers.StudentListView.as_view(),name='new_student'),
        path('students/activate/<int:pk>/',teachers.approve,name='approve'),
        path('quiz/add/', teachers.QuizCreateView.as_view(), name='quiz_add'),
        path('quiz/<int:pk>/', teachers.QuizUpdateView.as_view(), name='quiz_change'),
        path('quiz/<int:pk>/delete/', teachers.QuizDeleteView.as_view(), name='quiz_delete'),
        path('quiz/<int:pk>/results/', teachers.QuizResultsView.as_view(), name='quiz_results'),
        path('quiz/<int:pk>/question/add/', teachers.question_add, name='question_add'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/', teachers.question_change, name='question_change'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', teachers.QuestionDeleteView.as_view(), name='question_delete'),
        path('subject/', teachers.SubjectListView.as_view(), name='sub_list'),
        path('subject/add/',teachers.SubjectCreateView.as_view(),name = 'sub_add'),
        path('subject/del/<int:pk>/',teachers.SubjectDeleteView.as_view(),name = 'sub_del'),
    ], 'classroom'), namespace='teachers')),
]
