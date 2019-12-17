from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView
from django.utils.timezone import datetime
from ..decorators import student_required
from ..forms import StudentInterestsForm, StudentSignUpForm, TakeQuizForm
from ..models import Quiz, Student, TakenQuiz, User
from random import Random
import random
from django.db.models import Case, Count, When
class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Contact your teacher to activate your account before logging in')
        return redirect('login')


@method_decorator([login_required, student_required], name='dispatch')
class StudentInterestsView(UpdateView):
    model = Student
    form_class = StudentInterestsForm
    template_name = 'classroom/students/interests_form.html'
    success_url = reverse_lazy('students:quiz_list')

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)


@method_decorator([login_required, student_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'classroom/students/quiz_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_interests = student.interests.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=student_interests) \
                .exclude(pk__in=taken_quizzes) \
                .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'classroom/students/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_quizzes \
            .select_related('quiz', 'quiz__subject') \
            .order_by('quiz__name')
        return queryset

@login_required
@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user.student

    if student.quizzes.filter(pk=pk).exists():
        return render(request, 'students/taken_quiz.html')

    random.seed(student)

    answered_questions_lev = student.quiz_answers \
        .filter(answer__question__quiz=quiz) \
        .values_list('answer__question__level', flat=True)
    correct_question_lev = list(student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).values_list('answer__question__level', flat=True))
    answer_questions_lev = list(student.quiz_answers \
        .filter(answer__question__quiz=quiz) \
        .values_list('answer__question__level', flat=True))
    answers = list(student.quiz_answers.filter(answer__question__quiz=quiz).values_list('answer__id', flat=True))
    correct_answers = list(student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).values_list('answer__id', flat=True))
    total_questions = quiz.quiz_total_questions
    print(correct_question_lev)
    if len(answers)==0:
        lev = 3;
    else:
        lev = answered_questions_lev.last()
        print(lev)
    unanswered_questions = student.get_unanswered_questions(quiz,answers,correct_answers,lev)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round((((total_questions-len(answers)) - 1) / total_questions) * 100)
    question = unanswered_questions.first()
    # print(answer_questions)
    print('total=',total_questions)
    print(answers)
    print(correct_answers)
    print(len(answers))
    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():

            with transaction.atomic():

                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()

                if student.get_unanswered_questions(quiz,answers,correct_answers,lev).exists() and len(answers)+1<total_questions:
                    return redirect('students:take_quiz', pk)
                elif len(answers)+1>=total_questions:
                    correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    score=0;
                    for i in correct_question_lev:
                        if i==1:
                            score = score +1;
                        if i==2:
                            score = score +2;
                        if i==3:
                            score = score +3;
                        if i==4:
                            score = score +6;
                        if i==5:
                            score = score +9;
                    total_score=0
                    for i in answer_questions_lev:
                        if i==1:
                            total_score = total_score +1;
                        if i==2:
                            total_score = total_score +2;
                        if i==3:
                            total_score = total_score +3;
                        if i==4:
                            total_score = total_score +6;
                        if i==5:
                            total_score = total_score +9;
                    percentage = round((score/total_score * 100),2)
                    view_results(request,pk=pk)
                    TakenQuiz.objects.create(student=student, quiz=quiz, score=percentage,total_marks=total_score,obtained_marks=score)


                    return redirect('students:results',pk=pk)
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'classroom/students/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })

@login_required
@student_required
def view_results(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user.student
    user = request.user

    answered_questions_lev = student.quiz_answers \
        .filter(answer__question__quiz=quiz) \
        .values_list('answer__question__level', flat=True)
    correct_question_lev = list(student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).values_list('answer__question__level', flat=True))
    answer_questions_lev = list(student.quiz_answers \
        .filter(answer__question__quiz=quiz) \
        .values_list('answer__question__level', flat=True))
    answerss = list(student.quiz_answers.filter(answer__question__quiz=quiz).values_list('answer__id', flat=True))
    correct_answers = list(student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).values_list('answer__id', flat=True))
    answered_questions = student.quiz_answers.filter(answer__question__quiz=quiz).values_list('answer__question__text', flat=True)
    correct_ques = student.quiz_answers.filter(answer__question__quiz=quiz,answer__is_correct=True).values_list('answer__question__text', flat=True)
    answers = student.quiz_answers.filter(answer__question__quiz=quiz).values_list('answer__text', flat=True)
    score=0;
    for i in correct_question_lev:
        if i==1:
            score = score +1;
        if i==2:
            score = score +2;
        if i==3:
            score = score +3;
        if i==4:
            score = score +6;
        if i==5:
            score = score +9;
    total_score=0
    for i in answer_questions_lev:
        if i==1:
            total_score = total_score +1;
        if i==2:
            total_score = total_score +2;
        if i==3:
            total_score = total_score +3;
        if i==4:
            total_score = total_score +6;
        if i==5:
            total_score = total_score +9;
    print(answerss)
    print(correct_answers)
    check = list(set(answerss).intersection(correct_answers))
    print(check)
    Marks = []
    marks_graph=[]
    for x,y in zip(answerss,answer_questions_lev):
        if x in check:
            if y==1:
                Marks.append('+1')
            elif y ==2:
                Marks.append('+2')
            elif y ==3:
                Marks.append('+3')
            elif y ==4:
                Marks.append('+6')
            elif y ==5:
                Marks.append('+9')
        elif x not in check:
            Marks.append('+0')
    fname = user.first_name
    lname = user.last_name
    username = user.username
    quiz = quiz.name
    print(quiz)
    total_ques = len(answers)

    percentage = round((score/total_score * 100),2)
    print(Marks)
    if percentage <= 32.0:
        messages.warning(request, 'Your obtained marks in %s was %s out of %s marks.' % (quiz, score,total_score))
    elif percentage <= 60 and percentage>32:
        messages.success(request, 'You completed the quiz %s with second division! You obtained marks was %s out of %s marks.' % (quiz, score,total_score))
    elif percentage <= 80 and percentage>60:
        messages.success(request, 'You completed the quiz %s with first division! You obtained marks was %s out of %s marks.' % (quiz, score,total_score))
    elif percentage>80:
        messages.success(request, 'You completed the quiz %s with  distinction! You obtained marks was %s out of %s marks.' % (quiz, score,total_score))
    zippedList = zip(answered_questions,answer_questions_lev,answers,Marks)

    return render(request, 'classroom/students/results.html', {
        'zippedList':zippedList,
        'pk':pk,
        'score':score,
        'total_score':total_score,
        'percentage':percentage,
        'fname':fname,
        'lname':lname,
        'username':username,
        'quiz':quiz,
        'total_ques':total_ques,
    })

@login_required
@student_required
def results_graph(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user.student
    user = request.user

    answered_questions_lev = student.quiz_answers \
        .filter(answer__question__quiz=quiz) \
        .values_list('answer__question__level', flat=True)
    correct_question_lev = list(student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).values_list('answer__question__level', flat=True))
    answer_questions_lev = list(student.quiz_answers \
        .filter(answer__question__quiz=quiz) \
        .values_list('answer__question__level', flat=True))
    answerss = list(student.quiz_answers.filter(answer__question__quiz=quiz).values_list('answer__id', flat=True))
    correct_answers = list(student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).values_list('answer__id', flat=True))
    answered_questions = student.quiz_answers.filter(answer__question__quiz=quiz).values_list('answer__question__text', flat=True)
    correct_ques = student.quiz_answers.filter(answer__question__quiz=quiz,answer__is_correct=True).values_list('answer__question__text', flat=True)
    answers = student.quiz_answers.filter(answer__question__quiz=quiz).values_list('answer__text', flat=True)
    score=0;
    for i in correct_question_lev:
        if i==1:
            score = score +1;
        if i==2:
            score = score +2;
        if i==3:
            score = score +3;
        if i==4:
            score = score +6;
        if i==5:
            score = score +9;
    total_score=0
    for i in answer_questions_lev:
        if i==1:
            total_score = total_score +1;
        if i==2:
            total_score = total_score +2;
        if i==3:
            total_score = total_score +3;
        if i==4:
            total_score = total_score +6;
        if i==5:
            total_score = total_score +9;

    print(answerss)
    print(correct_answers)
    check = list(set(answerss).intersection(correct_answers))
    print(check)
    Marks = []

    for x,y in zip(answerss,answer_questions_lev):
        if x in check:
            if y==1:
                Marks.append(1)
            elif y==2:
                Marks.append(2)
            elif y==3:
                Marks.append(3)
            elif y ==4:
                Marks.append(6)
            elif y ==5:
                Marks.append(9)

        elif x not in check:
            Marks.append(0)
    print(Marks)
    marks_graph=[]
    i=0;
    while(i<len(Marks)):
        if i>0:
            marks_graph.append(marks_graph[i-1]+Marks[i]);
        elif i==0:
            marks_graph.append(Marks[i])
        i=i+1;
    print('Marks=',marks_graph)



    num =[]
    i=1;
    while (i<=len(answers)):
        num.append(i)
        i=i+1
    print(num)
    fname = user.first_name
    lname = user.last_name
    username = user.username
    quiz = quiz.name
    print(quiz)
    total_ques = len(answers)
    percentage = round((score/total_score * 100),2)
    data={
        'pk':pk,
        'score':score,
        'total_score':total_score,
        'percentage':percentage,
        'fname':fname,
        'lname':lname,
        'username':username,
        'quiz':quiz,
        'total_ques':total_ques,
        'answers':answers,
        'answer_questions_lev':answer_questions_lev,
        'Marks':Marks,
        'num':num,
        'marks_graph':marks_graph
    }
    return render(request,'classroom/students/results_graph.html',data)
