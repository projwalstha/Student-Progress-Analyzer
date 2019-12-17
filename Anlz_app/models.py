from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Case, Count, When
import random

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Subject(models.Model):
    SubOwner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default='#007bff')

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)

    def get_absolute_url(self):
        return reverse("teachers:sub_list")

class Quiz(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    quiz_total_questions = models.IntegerField(default=10)
    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=500)
    level = models.IntegerField("Level",default=1,validators=[MaxValueValidator(5), MinValueValidator(1)])

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    interests = models.ManyToManyField(Subject, related_name='interested_students')

    def get_unanswered_questions(self, quiz,answers,correct_answers,lev):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        list_of_ids= list(quiz.questions.values_list('id', flat=True))
        q = quiz.questions.filter(pk__in=list_of_ids)
        random.shuffle(list_of_ids)
        clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(list_of_ids)])
        ordering = 'CASE %s END' % clauses
        ques = quiz.questions.filter(pk__in=list_of_ids).extra(select={'ordering': ordering}, order_by=('ordering',))



        if len(answers)<5:
            questions = quiz.questions.filter(pk__in=list_of_ids,level=lev).extra(select={'ordering': ordering}, order_by=('ordering',)).exclude(pk__in=answered_questions)

            print(1)
        elif len(list(set(answers[-5:]).intersection(correct_answers[-5:])))>=3 and len(answers)==5:
            questions = quiz.questions.filter(pk__in=list_of_ids,level=lev+1).extra(select={'ordering': ordering}, order_by=('ordering',)).exclude(pk__in=answered_questions)
            print(2)
        elif len(list(set(answers[-5:]).intersection(correct_answers[-5:])))<3 and len(answers)==5:
            questions = quiz.questions.filter(pk__in=list_of_ids,level=lev-1).extra(select={'ordering': ordering}, order_by=('ordering',)).exclude(pk__in=answered_questions)
            print(3)
        if len(list(set(answers[-2:]).intersection(correct_answers[-2:])))==2 and len(answers)>=6:
            if lev==5:
                questions = quiz.questions.filter(pk__in=list_of_ids,level=5).extra(select={'ordering': ordering}, order_by=('ordering',)).exclude(pk__in=answered_questions)
                print(5)
            elif lev<5:
                questions = quiz.questions.filter(pk__in=list_of_ids,level=lev+1).extra(select={'ordering': ordering}, order_by=('ordering',)).exclude(pk__in=answered_questions)
                print(6)

        if len(list(set(answers[-2:]).intersection(correct_answers[-2:])))!=2 and len(answers)>=6:
            if lev==1:
                 questions = quiz.questions.filter(pk__in=list_of_ids,level=1).extra(select={'ordering': ordering}, order_by=('ordering',)).exclude(pk__in=answered_questions)
                 print(7)
            elif len(list(set(answers[-2:]).intersection(correct_answers[-1:])))==1:
                 questions = quiz.questions.filter(pk__in=list_of_ids,level=lev).extra(select={'ordering': ordering}, order_by=('ordering',)).exclude(pk__in=answered_questions)
                 print(8)
            elif len(list(set(answers[-2:]).intersection(correct_answers[-2:])))==0:
                questions = quiz.questions.filter(pk__in=list_of_ids,level=lev-1).extra(select={'ordering': ordering}, order_by=('ordering',)).exclude(pk__in=answered_questions)
                print(9)


        # while (len(answers)<=3):
        #         lev=3;
        #
        #         if len(list(set(answers[-3:]).intersection(correct_answers[-3:])))>=2 and len(answers)==3:
        #             lev=lev+1;
        #             break;
        #         elif len(list(set(answers[-3:]).intersection(correct_answers[-3:])))<2 and len(answers)==3:
        #             lev=lev-1;
        #             break;
        # lev=lev
        # while(len(answers)>3 and len(answers)<=6):
        #         lev=lev;
        #         if len(list(set(answers[-3:]).intersection(correct_answers[-3:])))>=2 and len(answers)==6:
        #             lev=lev+1
        #             break;
        #         elif len(list(set(answers[-3:]).intersection(correct_answers[-3:])))<2 and len(answers)==6:
        #             lev=lev-1
        #             break;
        # lev=lev
        # i=6;
        # while(len(answers)>i and len(answers)<=i+3 and i<=100):
        #         lev=lev
        #         if lev==1 or lev==5:
        #             lev=lev
        #             continue
        #         elif len(list(set(answers[-3:]).intersection(correct_answers[-3:])))>=2 and len(answers)==i+3:
        #             lev=lev+1
        #             continue
        #         elif len(list(set(answers[-3:]).intersection(correct_answers[-3:])))<2 and len(answers)==i+3:
        #             lev=lev-1
        #             continue
        #         i=i+3;
        #
        # lev=lev


        return questions

class TakenQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    total_marks = models.IntegerField(default=0)
    obtained_marks = models.IntegerField(default=0)


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')
