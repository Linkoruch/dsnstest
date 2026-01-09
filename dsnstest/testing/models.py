from django.db import models


class Test(models.Model):
    title = models.CharField("Назва тесту", max_length=255)
    description = models.TextField("Опис", blank=True)
    is_published = models.BooleanField("Опубліковано", default=False)
    created_at = models.DateTimeField("Створено", auto_now_add=True)

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тести"

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField("Текст питання")

    def __str__(self) -> str:
        return f"{self.test.title}: {self.text[:50]}"


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField("Варіант відповіді", max_length=500)
    is_correct = models.BooleanField("Правильна відповідь", default=False)

    def __str__(self) -> str:
        return self.text


class Attempt(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="attempts")
    full_name = models.CharField("ПІБ/позивний", max_length=255)
    score = models.PositiveIntegerField("Правильних", default=0)
    total = models.PositiveIntegerField("Всього", default=0)
    created_at = models.DateTimeField("Час проходження", auto_now_add=True)

    class Meta:
        verbose_name = "Результат тесту"
        verbose_name_plural = "Результати тестів"

    def __str__(self) -> str:
        return f"{self.full_name} – {self.test.title} ({self.score}/{self.total})"


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("attempt", "question")
