from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Prefetch
from .models import Test, Question, AnswerOption, Attempt, AttemptAnswer


def test_list(request):
    tests = Test.objects.filter(is_published=True).order_by("-created_at")
    return render(request, "testing/test_list.html", {"tests": tests})


def test_start(request, test_id: int):
    test = get_object_or_404(Test, id=test_id, is_published=True)

    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        if not full_name:
            return render(request, "testing/test_start.html", {"test": test, "error": "Вкажіть ПІБ/позивний"})

        # збережемо у сесії, щоб не світити в URL
        request.session["full_name"] = full_name
        return redirect("testing:test_take", test_id=test.id)

    return render(request, "testing/test_start.html", {"test": test})


def test_take(request, test_id: int):
    test = get_object_or_404(Test, id=test_id, is_published=True)
    full_name = (request.session.get("full_name") or "").strip()

    if not full_name:
        return redirect("testing:test_start", test_id=test.id)

    questions = (
        Question.objects.filter(test=test)
        .prefetch_related(Prefetch("options", queryset=AnswerOption.objects.order_by("id")))
        .order_by("id")
    )

    if request.method == "POST":
        attempt = Attempt.objects.create(test=test, full_name=full_name, total=questions.count())

        score = 0
        for q in questions:
            selected_id = request.POST.get(f"q_{q.id}")
            if not selected_id:
                continue

            selected = get_object_or_404(AnswerOption, id=int(selected_id), question=q)
            AttemptAnswer.objects.create(attempt=attempt, question=q, selected_option=selected)

            if selected.is_correct:
                score += 1

        attempt.score = score
        attempt.save()

        # очистимо ПІБ із сесії після завершення
        request.session.pop("full_name", None)

        return redirect("testing:result", attempt_id=attempt.id)

    return render(request, "testing/test_take.html", {"test": test, "questions": questions, "full_name": full_name})


def result_view(request, attempt_id: int):
    attempt = get_object_or_404(
        Attempt.objects.select_related("test").prefetch_related("answers__question", "answers__selected_option"),
        id=attempt_id
    )

    questions = (
        Question.objects.filter(test=attempt.test)
        .prefetch_related(Prefetch("options", queryset=AnswerOption.objects.order_by("id")))
        .order_by("id")
    )

    selected_map = {a.question_id: a.selected_option_id for a in attempt.answers.all()}

    return render(
        request,
        "testing/result.html",
        {"attempt": attempt, "questions": questions, "selected_map": selected_map},
    )

