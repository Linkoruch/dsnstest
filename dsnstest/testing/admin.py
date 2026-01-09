from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet

from .models import Test, Question, AnswerOption, Attempt, AttemptAnswer


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4


class AnswerOptionInlineFormSet(BaseInlineFormSet):
    pass


AnswerOptionFormSet = inlineformset_factory(
    Question,
    AnswerOption,
    fields=("text", "is_correct"),
    extra=2,
    can_delete=True,
    formset=AnswerOptionInlineFormSet,
)


class QuestionInlineFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.nested = AnswerOptionFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix=f"{form.prefix}-{AnswerOptionFormSet.get_default_prefix()}",
        )


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerOptionInline]
    list_display = ("id", "test", "text")


class QuestionInline(admin.StackedInline):
    model = Question
    formset = QuestionInlineFormSet
    fields = ("text",)
    extra = 0
    show_change_link = False
    template = "admin/testing/question_inline.html"


class TestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_published", "created_at")
    list_filter = ("is_published",)
    list_display_links = ("id", "title")
    actions = None  # disable bulk actions
    inlines = [QuestionInline]
    # search_fields = ("title",)  # поле пошуку прибрали

    def save_formset(self, request, form, formset, change):
        # Save questions first
        instances = formset.save(commit=False)
        for obj in instances:
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()

        # Save nested answers for each question
        for inline_form in formset.forms:
            nested = getattr(inline_form, "nested", None)
            if nested is None:
                continue
            nested.instance = inline_form.instance
            nested_instances = nested.save(commit=False)
            for obj in nested_instances:
                obj.question = inline_form.instance
                obj.save()
            for obj in getattr(nested, "deleted_objects", []):
                obj.delete()

        formset.save_m2m()


# ✅ Реєструємо тільки потрібне
admin.site.register(Test, TestAdmin)   # Тести
admin.site.register(Attempt)           # Результати тестів


# ✅ Прибираємо "Групи"
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


# ✅ Прибираємо технічні моделі (щоб не показувались)
for m in (AnswerOption, AttemptAnswer, Question):
    try:
        admin.site.unregister(m)
    except admin.sites.NotRegistered:
        pass


# ✅ Перереєструємо "Користувачі" без груп і прав (щоб прибрати поле фільтру)
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    exclude = ("groups", "user_permissions",)
    filter_horizontal = ()
