from app.core.parser import ParsedDocument, ParsedSection
from app.core.retriever import RAGRetriever


def test_retriever_selects_relevant_sections_by_query():
    document = ParsedDocument(
        title="Doc",
        sections=[
            ParsedSection(
                heading="Heart",
                content="Hypertension and blood pressure management.",
                level=2,
                start_pos=0,
                end_pos=50,
            ),
            ParsedSection(
                heading="Lungs",
                content="Asthma and pulmonary function treatment.",
                level=2,
                start_pos=51,
                end_pos=100,
            ),
        ],
        source_text="Hypertension and blood pressure management. "
                    "Asthma and pulmonary function treatment.",
    )

    retriever = RAGRetriever()
    results = retriever.retrieve_relevant_sections(
        document=document,
        query="blood pressure hypertension",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].heading == "Heart"
