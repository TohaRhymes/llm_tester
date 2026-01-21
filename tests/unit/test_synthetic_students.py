from app.core.synthetic_students import SyntheticStudentGenerator
from app.models.schemas import Exam, ExamConfig, Question, QuestionMeta


def build_exam():
    return Exam(
        exam_id="synthetic",
        questions=[
            Question(
                id="q1",
                type="single_choice",
                stem="What is 2+2?",
                options=["3", "4", "5"],
                correct=[1],
                source_refs=[],
                meta=QuestionMeta(difficulty="easy", tags=[]),
            ),
            Question(
                id="q2",
                type="multiple_choice",
                stem="Select even numbers",
                options=["1", "2", "3", "4"],
                correct=[1, 3],
                source_refs=[],
                meta=QuestionMeta(difficulty="medium", tags=[]),
            ),
            Question(
                id="q3",
                type="open_ended",
                stem="Explain gravity",
                reference_answer="Gravity is the force that attracts objects with mass.",
                rubric=["Mentions force", "Mentions mass"],
                source_refs=[],
                meta=QuestionMeta(difficulty="easy", tags=[]),
            ),
        ],
        config_used=ExamConfig(provider="local"),
    )


def test_generate_48_students():
    exam = build_exam()
    generator = SyntheticStudentGenerator(seed=123)
    students = generator.generate_students(exam, count=48)
    assert len(students) == 48
    assert all(len(s["answers"]) == len(exam.questions) for s in students)


def test_generation_is_deterministic():
    exam = build_exam()
    generator_a = SyntheticStudentGenerator(seed=42)
    generator_b = SyntheticStudentGenerator(seed=42)

    students_a = generator_a.generate_students(exam, count=5)
    students_b = generator_b.generate_students(exam, count=5)

    assert students_a[0]["answers"] == students_b[0]["answers"]
