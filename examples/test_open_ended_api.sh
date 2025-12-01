#!/bin/bash
# Demonstration of open-ended question API workflow

echo "=== Open-Ended Questions API Demo ==="
echo ""

# Step 1: Generate exam with open-ended questions
echo "Step 1: Generating exam with open-ended questions..."
echo ""

EXAM_RESPONSE=$(curl -s -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "# Hypertensive Disorders in Pregnancy\n\n## Preeclampsia\n\nPreeclampsia is a pregnancy complication characterized by high blood pressure and signs of damage to another organ system. The pathophysiology involves endothelial dysfunction caused by placental ischemia. This leads to systemic vasoconstriction, increased vascular permeability, and potential organ damage.\n\n### Diagnostic Criteria\n\nDiagnosis requires:\n- Blood pressure ≥140/90 mmHg on two occasions at least 4 hours apart\n- Occurring after 20 weeks of gestation\n- Accompanied by proteinuria (≥300 mg/24 hours) or other organ dysfunction\n\n### Management\n\nTreatment includes:\n- Antihypertensive medications (labetalol, nifedipine)\n- Magnesium sulfate for seizure prophylaxis\n- Delivery planning based on severity and gestational age",
    "config": {
      "total_questions": 3,
      "single_choice_ratio": 0.33,
      "multiple_choice_ratio": 0.0,
      "open_ended_ratio": 0.67,
      "difficulty": "medium"
    }
  }')

echo "Response received!"
echo ""

# Extract exam_id
EXAM_ID=$(echo $EXAM_RESPONSE | grep -o '"exam_id":"[^"]*' | cut -d'"' -f4)
echo "Generated Exam ID: $EXAM_ID"
echo ""

# Display questions
echo "Generated Questions:"
echo $EXAM_RESPONSE | python3 -m json.tool | grep -A 20 '"questions"'
echo ""

# Step 2: Find an open-ended question
echo "Step 2: Extracting open-ended question details..."
echo ""

OPEN_ENDED_Q=$(echo $EXAM_RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
for q in data['questions']:
    if q['type'] == 'open_ended':
        print(f\"Question ID: {q['id']}\")
        print(f\"Stem: {q['stem']}\")
        print(f\"Reference Answer: {q['reference_answer'][:100]}...\")
        print(f\"Rubric Criteria: {len(q['rubric'])} items\")
        for i, r in enumerate(q['rubric'], 1):
            print(f\"  {i}. {r}\")
        print(f\"Question ID (for grading): {q['id']}\")
        break
" 2>/dev/null)

echo "$OPEN_ENDED_Q"
echo ""

# Extract question ID for grading
QUESTION_ID=$(echo $EXAM_RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
for q in data['questions']:
    if q['type'] == 'open_ended':
        print(q['id'])
        break
" 2>/dev/null)

echo "Step 3: Submitting student answers for grading..."
echo ""

# Grade with good answer
echo "Test Case 1: Good Answer"
GRADE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/grade \
  -H "Content-Type: application/json" \
  -d "{
    \"exam_id\": \"$EXAM_ID\",
    \"answers\": [
      {
        \"question_id\": \"$QUESTION_ID\",
        \"text_answer\": \"Preeclampsia is caused by endothelial dysfunction resulting from placental ischemia. The diagnostic criteria include blood pressure ≥140/90 mmHg after 20 weeks gestation, along with proteinuria ≥300mg/24h. Management involves antihypertensive therapy such as labetalol or nifedipine, and magnesium sulfate for seizure prevention.\"
      }
    ]
  }")

echo "Grading Result:"
echo $GRADE_RESPONSE | python3 -m json.tool | grep -A 15 '"per_question"'
echo ""

echo "Summary:"
echo $GRADE_RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total Score: {data['summary']['score_percent']}%\")
for q in data['per_question']:
    print(f\"Question {q['question_id']}:\")
    print(f\"  Correct: {q['is_correct']}\")
    print(f\"  Score: {q['partial_credit']}\")
    print(f\"  Feedback: {q['feedback']}\")
" 2>/dev/null

echo ""
echo "=== Demo Complete ==="
echo ""
echo "Key Features Demonstrated:"
echo "1. ✓ Generate exam with open-ended questions (open_ended_ratio)"
echo "2. ✓ AI generates reference answers and rubrics"
echo "3. ✓ Submit text answers (text_answer field)"
echo "4. ✓ AI-powered grading with rubric evaluation"
echo "5. ✓ Detailed feedback for student improvement"
echo ""
echo "Exam saved to: out/exam_$EXAM_ID.json"
echo "Grading saved to: out/grade_$EXAM_ID.json"
